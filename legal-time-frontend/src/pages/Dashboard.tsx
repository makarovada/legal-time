import React, { useEffect, useState, useContext } from 'react';
import { Grid, Card, CardContent, Typography } from '@mui/material';
import { Bar } from 'react-chartjs-2';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosInstance'; // ← вот наш новый клиент

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({ totalHours: 0, pendingTimesheets: 0 });
  const { role } = useContext(AuthContext)!;

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/time-entries/stats'); // ← просто относительный путь!
        setStats(res.data);
      } catch (err: any) {
        console.error('Ошибка загрузки статистики:', err);
        // setError(err.response?.data?.detail || 'Не удалось загрузить статистику');
      } finally {
        // setLoading(false);
      }
    };
  fetchStats();
}, []);

  const chartData = {
    labels: ['Consultation', 'Court', 'Docs'], // Типы активностей
    datasets: [{ label: 'Hours', data: [10, 20, 15], backgroundColor: '#1976d2' }],
  };


  return (
    <Grid container spacing={3}>
      <Grid size={12}>
        <Typography variant="h4">Dashboard</Typography>
      </Grid>

      <Grid size={4}>
        <Card>
          <CardContent>
            <Typography>Total Hours: {stats.totalHours}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={4}>
        <Card>
          <CardContent>
            <Typography>Pending Timesheets: {stats.pendingTimesheets}</Typography>
          </CardContent>
        </Card>
      </Grid>

      {role === 'admin' && (
        <Grid size={4}>
          <Card>
            <CardContent>
              <Typography>Admin Stats...</Typography>
            </CardContent>
          </Card>
        </Grid>
      )}

      <Grid size={12}>
        <Bar data={chartData} options={{ responsive: true }} />
      </Grid>
    </Grid>
  );
};

export default Dashboard;