import React, { useEffect, useState } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { Grid, Paper, Typography } from '@mui/material';
import axios from 'axios';

interface Matter {
  id: number;
  code: string;
  name: string;
  status: 'new' | 'in_progress' | 'closed';
}

const Matters: React.FC = () => {
  const [columns, setColumns] = useState({
    new: [] as Matter[],
    in_progress: [] as Matter[],
    closed: [] as Matter[],
  });

  useEffect(() => {
    const fetchMatters = async () => {
      const res = await axios.get('http://localhost:8000/matters');
      const grouped = res.data.reduce((acc: any, matter: Matter) => {
        acc[matter.status] = [...(acc[matter.status] || []), matter];
        return acc;
      }, {});
      setColumns(grouped);
    };
    fetchMatters();
  }, []);

  const onDragEnd = (result: any) => {
    // Логика перемещения: обновить status на backend и перерендерить
    // ...
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Grid container spacing={2}>
        {Object.keys(columns).map((col) => (
          <Grid size={4} key={col}>   // ← size={4}
            <Typography>{col.toUpperCase()}</Typography>
            <Droppable droppableId={col}>
              {(provided) => (
                <Paper {...provided.droppableProps} ref={provided.innerRef}>
                  {/* ... */}
                  {provided.placeholder}
                </Paper>
              )}
            </Droppable>
          </Grid>
        ))}
      </Grid>
    </DragDropContext>
  );
};

export default Matters;