// src/pages/Login.tsx — исправленная версия
import React, { useState, useContext } from 'react';
import { Button, TextField, Container, Typography, Alert } from '@mui/material';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const authContext = useContext(AuthContext);
  const navigate = useNavigate();

  // Защита от undefined контекста
  if (!authContext) {
    return (
      <Container maxWidth="sm">
        <Alert severity="error">Ошибка: AuthContext не инициализирован</Alert>
      </Container>
    );
  }

  const { login } = authContext;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const payload = {
        username,          // или email — попробуй оба варианта
        password,
        grant_type: "password",   // раскомментируй, если нужно
      };

      const res = await axios.post('http://localhost:8000/auth/login', payload, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',  // важно для OAuth2PasswordRequestForm
        },
      });

      login(res.data.access_token);
      navigate('/');
    } catch (err: any) {
      // ← здесь главная проблема была
      const errorData = err.response?.data;

      // FastAPI 422 возвращает примерно такой объект:
      // { detail: [ { loc: ["body", "username"], msg: "field required", type: "missing" } ] }
      // или просто { detail: "Incorrect username or password" }

      const errorMessage =
        errorData?.detail?.[0]?.msg || // для детализированных ошибок
        errorData?.detail ||           // для простых строк
        'Ошибка авторизации. Проверьте данные';

      setError(errorMessage);
      console.error('Login error details:', errorData);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        Вход в LegalTime
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <form onSubmit={handleSubmit}>
        <TextField
          label="Имя пользователя"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
          margin="normal"
          required
        />
        <TextField
          label="Пароль"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
          margin="normal"
          required
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          sx={{ mt: 3 }}
        >
          Войти
        </Button>
      </form>
    </Container>
  );
};

export default Login;