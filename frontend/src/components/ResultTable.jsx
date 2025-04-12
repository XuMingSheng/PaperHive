import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography
} from '@mui/material';

const ResultTable = ({ tableData }) => (
  tableData.columns.length > 0 && (
    <>
      <Typography variant="h6" mt={4} mb={2}>Summary Table</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {tableData.columns.map((col, idx) => (
                <TableCell key={idx}><strong>{col}</strong></TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {tableData.rows.map((row, idx) => (
              <TableRow key={idx}>
                {row.map((cell, i) => (
                  <TableCell key={i}>{cell}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  )
);

export default ResultTable;