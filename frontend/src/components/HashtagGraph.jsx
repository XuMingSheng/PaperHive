import React, { useEffect, useState, useRef, useMemo } from "react";
import { Box, IconButton, Tooltip, Typography, Modal } from "@mui/material";
import FullscreenIcon from "@mui/icons-material/Fullscreen";
import FullscreenExitIcon from "@mui/icons-material/FullscreenExit";
import ForceGraph2D from "react-force-graph-2d";
import { fetchGraph } from "../api/hashtagApi";

const HashtagGraph = ({ tags, steps = 2 }) => {
  const [graphData, setGraphData] = useState({ nodes: [], links: []});
  const [expanded, setExpanded] = useState(false);
  const containerRef = useRef();

  useEffect(
    ()=>{
      if (tags.length == 0) return;
      
      fetchGraph(tags)
        .then(data => {
          const nodes = data.nodes.map(tag => ({id: tag}))
          const links = data.edges.map(edge => ({
            source: edge.src,
            target: edge.dst,
            value: edge.weight || 1,
          }));
          setGraphData({ nodes, links });
        })
    }, 
    [tags, steps]
  );

  const maxWeight = useMemo(() => {
    if (!graphData.links || graphData.links.length === 0) return 1;
    return Math.max(...graphData.links.map((link) => link.value || 1));
  }, [graphData.links]);

const renderGraph = (width, height) => (
    <ForceGraph2D
      graphData={graphData}
      width={width}
      height={height}
      
      // Remove direction particles and arrows
      linkDirectionalParticles={0}
      linkDirectionalArrowLength={0}

      // Tag-style text labels (bold + chip look)
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.id;
        const fontSize = 12 / globalScale;
        ctx.font = `bold ${fontSize}px Sans-Serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
  
        const paddingX = 4;
        const paddingY = 2;
        const textWidth = ctx.measureText(label).width;
        const boxWidth = textWidth + paddingX * 2;
        const boxHeight = fontSize + paddingY * 2;
  
        // Draw background like a chip
        ctx.fillStyle = "#1976d2"; // primary blue
        ctx.beginPath();
        ctx.roundRect?.(node.x - boxWidth / 2, node.y - boxHeight / 2, boxWidth, boxHeight, 6);
        ctx.fill();
  
        // Draw text
        ctx.fillStyle = "#fff";
        ctx.fillText(label, node.x, node.y + 1);
      }}
      
      // Edge config
      linkWidth={(link) => Math.log(link.value || 1) + 1}
      linkColor={(link) => {
        const weight = link.value || 1;
        const intensity = Math.min(1, weight / maxWeight);  // scale to 0–1
        const r = Math.floor(255 * intensity);
        const g = Math.floor(255 * (1 - intensity));
        const b = 0;
        return `rgba(${r},${g},${b},0.8)`;  // yellow to red
      }}
      linkLabel={(link) => `Weight: ${link.value}`}
      linkHoverPrecision={5}
    />
  );

  return (
    <>
      {/* 📦 Preview Graph */}
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

      {/* 🖼️ Fullscreen Graph */}
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

          <Box sx={{ width: "100%", height: "100%" }}>
            {renderGraph(undefined, undefined)}
          </Box>
        </Box>
      </Modal>
    </>
  );
};

export default HashtagGraph