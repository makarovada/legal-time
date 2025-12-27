// src/pages/Timesheets.tsx
import React, { useState, useEffect, useContext } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  Button,
  TextField,
  Box,
  IconButton,
  Chip,
  Tooltip,
  Alert,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import TimesheetModal from '../components/TimesheetModal';

interface TimeEntry {
  id: number;
  hours: number;
  description: string | null;
  date: string;
  matter_id: number;
  activity_type_id: number;
  rate_id: number | null;
  employee_id: number;
  status: string; // draft, approved, etc.
}

const Timesheets: React.FC = () => {
  const [timeEntries, setTimeEntries] = useState<TimeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('');
  const [openModal, setOpenModal] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<TimeEntry | null>(null);

  const { role } = useContext(AuthContext)!;

  const isManagerOrAdmin = role === 'manager' || role === 'admin';

  useEffect(() => {
    fetchTimeEntries();
  }, [isManagerOrAdmin]);

  const fetchTimeEntries = async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = isManagerOrAdmin ? '/time-entries/all' : '/time-entries/';
      const res = await axios.get(`http://localhost:8000${endpoint}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        params: {
          skip: 0,
          limit: 200, // можно сделать пагинацию позже
        },
      });
      setTimeEntries(res.data);
    } catch (err: any) {
      setError('Не удалось загрузить записи времени: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    if (!window.confirm('Утвердить эту запись времени?')) return;

    try {
      await axios.patch(`http://localhost:8000/time-entries/${id}/approve`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      fetchTimeEntries();
    } catch (err) {
      setError('Не удалось утвердить запись');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Удалить запись?')) return;

    try {
      await axios.delete(`http://localhost:8000/time-entries/${id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      fetchTimeEntries();
    } catch (err) {
      setError('Не удалось удалить запись');
    }
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'date', headerName: 'Дата', width: 120 },
    { field: 'hours', headerName: 'Часы', width: 90, type: 'number' },
    { field: 'description', headerName: 'Описание', flex: 1, minWidth: 200 },
    { field: 'matter_id', headerName: 'Дело ID', width: 90 },
    { field: 'activity_type_id', headerName: 'Тип активности ID', width: 130 },
    {
      field: 'status',
      headerName: 'Статус',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={
            params.value === 'approved' ? 'success' :
            params.value === 'draft' ? 'default' : 'warning'
          }
          size="small"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Действия',
      width: 180,
      renderCell: (params) => (
        <>
          <Tooltip title="Редактировать">
            <IconButton onClick={() => { setSelectedEntry(params.row); setOpenModal(true); }}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          {isManagerOrAdmin && params.row.status !== 'approved' && (
            <Tooltip title="Утвердить">
              <IconButton onClick={() => handleApprove(params.row.id)} color="success">
                <CheckCircleIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}

          <Tooltip title="Удалить">
            <IconButton onClick={() => handleDelete(params.row.id)} color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </>
      ),
    },
  ];

  return (
    <Box sx={{ p: 3, height: 'calc(100vh - 64px)' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <TextField
          label="Поиск (по описанию или дате)"
          variant="outlined"
          size="small"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          sx={{ width: 320 }}
        />
        <Button
          variant="contained"
          onClick={() => { setSelectedEntry(null); setOpenModal(true); }}
        >
          Создать запись
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <DataGrid
        rows={timeEntries.filter(entry =>
          filter === '' ||
          entry.description?.toLowerCase().includes(filter.toLowerCase()) ||
          entry.date.includes(filter)
        )}
        columns={columns}
        loading={loading}
        pageSizeOptions={[10, 25, 50, 100]}
        density="compact"
        disableRowSelectionOnClick
        sx={{
          '& .MuiDataGrid-columnHeader': { backgroundColor: '#f5f5f5' },
        }}
      />

      <TimesheetModal
        open={openModal}
        onClose={() => {
          setOpenModal(false);
          setSelectedEntry(null);
          fetchTimeEntries();
        }}
        initialData={selectedEntry}
        isManagerOrAdmin={isManagerOrAdmin}
      />
    </Box>
  );
};

export default Timesheets;