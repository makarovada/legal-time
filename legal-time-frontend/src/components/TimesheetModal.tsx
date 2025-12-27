// src/components/TimesheetModal.tsx
import React, { useEffect, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Box,
  Alert,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import {
  useForm,
  Controller,
  SubmitHandler,
  Resolver,
} from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import axios from 'axios';
import { ru } from 'date-fns/locale';

interface TimeEntryFormData {
  hours: number;
  description: string | null;
  date: Date | null;
  matter_id: number;
  activity_type_id: number;
  rate_id: number | null;
}

interface DropdownItem {
  id: number;
  name?: string;
  code?: string;
  value?: number;
}

interface Props {
  open: boolean;
  onClose: () => void;
  initialData: any | null;
  isManagerOrAdmin: boolean;
}

// Yup-схема с совместимыми типами
const schema = yup.object({
  hours: yup
    .number()
    .required('Укажите количество часов')
    .positive('Часы должны быть положительными')
    .min(0.1, 'Минимум 0.1 часа')
    .typeError('Введите число'),
  description: yup.string().nullable(),
  date: yup
    .date()
    .required('Укажите дату')
    .nullable()
    .typeError('Неверный формат даты'),
  matter_id: yup
    .number()
    .required('Выберите дело')
    .min(1, 'Выберите дело'),
  activity_type_id: yup
    .number()
    .required('Выберите тип активности')
    .min(1, 'Выберите тип'),
  rate_id: yup.number().nullable(),
});

const TimesheetModal: React.FC<Props> = ({
  open,
  onClose,
  initialData,
  isManagerOrAdmin,
}) => {
  const [matters, setMatters] = useState<DropdownItem[]>([]);
  const [activityTypes, setActivityTypes] = useState<DropdownItem[]>([]);
  const [rates, setRates] = useState<DropdownItem[]>([]);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TimeEntryFormData>({
    resolver: yupResolver(schema) as Resolver<TimeEntryFormData>, // Явное приведение
    defaultValues: {
      hours: 1,
      description: null,
      date: new Date(),
      matter_id: 0,
      activity_type_id: 0,
      rate_id: null,
    },
  });

  useEffect(() => {
    if (open) {
      fetchDropdowns();
      reset(
        initialData
          ? {
              hours: initialData.hours ?? 1,
              description: initialData.description ?? null,
              date: initialData.date ? new Date(initialData.date) : null,
              matter_id: initialData.matter_id ?? 0,
              activity_type_id: initialData.activity_type_id ?? 0,
              rate_id: initialData.rate_id ?? null,
            }
          : {
              hours: 1,
              description: null,
              date: new Date(),
              matter_id: 0,
              activity_type_id: 0,
              rate_id: null,
            }
      );
    }
  }, [open, initialData, reset]);

  const fetchDropdowns = async () => {
    try {
      const [mattersRes, activityRes, ratesRes] = await Promise.all([
        axios.get('http://localhost:8000/matters/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        axios.get('http://localhost:8000/activity-types/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        axios.get('http://localhost:8000/rates/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
      ]);

      setMatters(mattersRes.data || []);
      setActivityTypes(activityRes.data || []);
      setRates(ratesRes.data || []);
    } catch (err) {
      console.error('Ошибка загрузки справочников', err);
      setSubmitError('Не удалось загрузить справочники');
    }
  };

  const onSubmit: SubmitHandler<TimeEntryFormData> = async (data) => {
    setSubmitError(null);

    const payload = {
      hours: data.hours,
      description: data.description ?? null,
      date: data.date instanceof Date ? data.date.toISOString().split('T')[0] : '',
      matter_id: data.matter_id,
      activity_type_id: data.activity_type_id,
      rate_id: data.rate_id ?? null,
    };

    try {
      if (initialData?.id) {
        await axios.put(`http://localhost:8000/time-entries/${initialData.id}`, payload, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
      } else {
        await axios.post('http://localhost:8000/time-entries/', payload, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
      }
      onClose();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setSubmitError(
        Array.isArray(detail) ? detail.map((e: any) => e.msg).join('; ') : detail || 'Ошибка сохранения'
      );
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {initialData ? 'Редактирование записи' : 'Новая запись времени'}
      </DialogTitle>

      <DialogContent>
        {submitError && <Alert severity="error" sx={{ mb: 2 }}>{submitError}</Alert>}

        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ru}>
          <Box component="form" sx={{ display: 'grid', gap: 2.5, mt: 1 }}>
            {/* Поля формы — вставьте сюда Controller'ы для date, hours, description, matter_id, activity_type_id, rate_id */}
            {/* Пример для date (остальные аналогично): */}
            <Controller
              name="date"
              control={control}
              render={({ field }) => (
                <DatePicker
                  {...field}
                  label="Дата"
                  value={field.value}
                  onChange={field.onChange}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      error: !!errors.date,
                      helperText: errors.date?.message,
                    },
                  }}
                />
              )}
            />

            {/* ... остальные Controller'ы ... */}

          </Box>
        </LocalizationProvider>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>Отмена</Button>
        <Button
          onClick={handleSubmit(onSubmit)}
          variant="contained"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Сохранение...' : initialData ? 'Сохранить' : 'Создать'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TimesheetModal;