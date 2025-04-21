import React, { useEffect, useState, useRef, useMemo, useLayoutEffect } from "react";
import { Box, IconButton, Tooltip, Typography, Modal } from "@mui/material";
import FullscreenIcon from "@mui/icons-material/Fullscreen";
import FullscreenExitIcon from "@mui/icons-material/FullscreenExit";
import ForceGraph3D from "react-force-graph-3d";
import * as THREE from 'three';
import * as d3 from 'd3';
import Graph from 'graphology';
import louvain from 'graphology-communities-louvain';
import { fetchGraph } from "../api/hashtagApi";

const HashtagGraph = ({ tags, steps = 2 }) => {
  const [graphData, setGraphData] = useState({ nodes: [], links: []});
  const [graphSize, setGraphSize] = useState({ width: 600, height: 400 });
  const [expanded, setExpanded] = useState(false);

  const containerRef = useRef();
  const fullscreenGraphRef = useRef()
  const fgRef = useRef();

  useLayoutEffect(() => {
    if (!expanded) return;

    const timeout = setTimeout(() => {
      if (fullscreenGraphRef.current) {
        const { offsetWidth, offsetHeight } = fullscreenGraphRef.current;
        setGraphSize({ width: offsetWidth, height: offsetHeight });
      }
    }, 0); // Wait until DOM has flushed layout
    
    return () => clearTimeout(timeout);
  }, [expanded]);

  // Load graph data from backend
  useEffect(
    ()=>{
      if (tags.length == 0) return;
      
      fetchGraph(tags)
        .then(data => {
          const nodes = data.nodes.map(tag => ({id: tag}))
          const links = data.edges.map(edge => ({
            source: edge.src,
            target: edge.dst,
            weight: edge.weight || 1,
            total_cnt: edge.total_cnt,
            cnt_by_year: edge.cnt_by_year
          }));
          setGraphData({ nodes, links });
        })
    }, 
    [tags, steps]
  );

  // Compute max link weight for edge color scaling
  const maxWeight = useMemo(() => {
    if (!graphData.links || graphData.links.length === 0) return 1;
    return Math.max(...graphData.links.map((link) => link.weight || 1));
  }, [graphData.links]);


  // Cluster nodes using Louvain and assign colors
  const clusteredGraph = useMemo(() => {
    const g = new Graph({ type: 'undirected' });
    graphData.nodes.forEach(node => g.addNode(node.id));
    graphData.links.forEach(link => {
      if (!g.hasEdge(link.source, link.target)) {
        g.addEdge(link.source, link.target, {
          weight: link.weight || 1,
          total_cnt: link.total_cnt || 0,
          cnt_by_year: link.cnt_by_year || {}
        });
      }
    });

    const communities = louvain(g);
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

    const clusteredNodes = graphData.nodes.map(node => {
      const cluster = communities[node.id] ?? 0;
      return {
        ...node,
        cluster,
        color: colorScale(cluster),
      };
    });

    return {
      nodes: clusteredNodes,
      links: graphData.links,
    };
  }, [graphData]);


  // Sprite-based node text (always faces camera)
  const nodeThreeObject = useMemo(() => (node) => {
    const label = `#${node.id}`;
    const fontSize = 42;
    const padding = 20;

    // Create canvas and measure text
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = `bold ${fontSize}px sans-serif`;
    const textWidth = ctx.measureText(label).width;

    // Set canvas size based on text
    canvas.width = textWidth + padding * 2;
    canvas.height = fontSize + padding * 2;

    // Draw with proper size
    // ctx.fillStyle = 'rgba(105, 105, 105, 0.75)';
    // ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.font = `bold ${fontSize}px sans-serif`;
    ctx.fillStyle = node.color || '#fff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, canvas.width / 2, canvas.height / 2);

    // Create sprite
    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    const material = new THREE.SpriteMaterial({ map: texture, depthWrite: false });
    const sprite = new THREE.Sprite(material);

    // Scale sprite to fit graph nicely
    const scaleFactor = 0.15;
    sprite.scale.set(canvas.width * scaleFactor, canvas.height * scaleFactor, 1);

    return sprite;
  }, []);

  // Expand node spacing using charge force
  useEffect(() => {
    if (!fgRef.current) return;
    fgRef.current.d3Force('charge')?.strength(-1500);
    fgRef.current.d3Force('collide')?.radius(15);
  }, [clusteredGraph]);

  const renderGraph = (width, height) => (
    <ForceGraph3D
      ref = {fgRef}
      graphData={clusteredGraph}
      backgroundColor="#0d1117"
      width={width}
      height={height}

      nodeAutoColorBy="cluster"
      nodeThreeObject={nodeThreeObject}

      // Remove direction particles and arrows
      linkDirectionalParticles={0}
      linkDirectionalArrowLength={0}
      
      // Edge config
      linkWidth={(link) => Math.log(Math.min(1, link.weight / maxWeight) + 1) + 1}
      linkMaterial={(link) => {
        const weight = link.weight || 1;
        const intensity = Math.min(1, weight / maxWeight);  // scale [0–1]
      
        const r = 255;
        const g = Math.floor(255 * (1 - intensity));  // from yellow to red
        const b = 0;
        const opacity = 0.5 + 0.5 * intensity;
      
        const material = new THREE.MeshBasicMaterial({
          color: new THREE.Color(`rgb(${r}, ${g}, ${b})`),
          transparent: true,
          opacity,
          depthWrite: false  // optional: makes lines more visible
        });
      
        return material;
      }}
      linkLabel={(link) => {
        const cnt_by_year = Object.entries(link.cnt_by_year)
          .sort((a, b) => b[0] - a[0]) 
          .map(([year, cnt]) => `${year}: ${cnt}`)
          .join(" | ")
        return `Total Papers: ${link.total_cnt} | ${cnt_by_year}`;
      }}
      linkHoverPrecision={5}
    />
  );

  return (
    <>
      {/* Preview Graph */}
      {!expanded && (
        <Box
          ref={containerRef}
          sx={{
            position: "relative",
            border: "1px solid #555",
            borderRadius: 1,
            width: "100%",
            height: 200,
            mb: 2,
          }}
        >
          {renderGraph(containerRef.current?.offsetWidth || 300, 200)}
          
          <Tooltip title="Expand Graph">
            <IconButton
              size="small"
              onClick={() => setExpanded(true)}
              sx={{
                position: "absolute",
                top: 4,
                right: 4,
                backgroundColor: "#fff9",
                zIndex: 2,
              }}
            >
              <FullscreenIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )}

      {/* Fullscreen Graph */}
      <Modal open={expanded} onClose={() => setExpanded(false)}>
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "90vw",
            height: "85vh",
            bgcolor: "background.paper",
            boxShadow: 24,
            p: 2,
            overflow: "hidden",
          }}
        >
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Hashtag Graph</Typography>
            <IconButton onClick={() => setExpanded(false)}>
              <FullscreenExitIcon />
            </IconButton>
          </Box>

          <Box ref={fullscreenGraphRef} sx={{ width: "100%", height: "100%" }}>
            {renderGraph(graphSize.width, graphSize.height)}
          </Box>
        </Box>
      </Modal>
    </>
  );
};

export default HashtagGraph