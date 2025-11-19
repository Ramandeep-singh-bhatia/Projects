import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Stack,
  Card,
  CardContent,
  IconButton,
  Chip,
  LinearProgress,
} from '@mui/material';
import { Add, Stop, Delete, FitnessCenter } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../store';
import {
  fetchWorkoutsByDate,
  deleteWorkout,
  completeWorkout,
  selectWorkouts,
  selectWorkoutLoading,
} from '../../features/workout/workoutSlice';
import MainLayout from '../../components/layout/MainLayout';
import AddWorkoutDialog from '../../components/workouts/AddWorkoutDialog';

const WorkoutsPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const workouts = useAppSelector(selectWorkouts);
  const loading = useAppSelector(selectWorkoutLoading);
  const [currentDate] = useState(new Date().toISOString().split('T')[0]);
  const [addDialogOpen, setAddDialogOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchWorkoutsByDate(currentDate));
  }, [currentDate, dispatch]);

  const handleCompleteWorkout = async (id: number) => {
    await dispatch(completeWorkout(id));
    dispatch(fetchWorkoutsByDate(currentDate));
  };

  const handleDeleteWorkout = async (id: number) => {
    if (window.confirm('Delete this workout?')) {
      await dispatch(deleteWorkout(id));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'success';
      case 'IN_PROGRESS': return 'warning';
      default: return 'default';
    }
  };

  const totalCaloriesBurned = workouts.reduce((sum, w) => sum + (w.totalCaloriesBurned || 0), 0);
  const totalDuration = workouts.reduce((sum, w) => sum + (w.totalDurationMinutes || 0), 0);

  return (
    <MainLayout>
      <Stack spacing={4}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Workout Tracking
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Track your workouts and monitor your fitness progress
          </Typography>
        </Box>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Card elevation={2} sx={{ flex: 1 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Workouts Today</Typography>
              <Typography variant="h4" fontWeight="bold">{workouts.length}</Typography>
            </CardContent>
          </Card>
          <Card elevation={2} sx={{ flex: 1 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Calories Burned</Typography>
              <Typography variant="h4" fontWeight="bold">{totalCaloriesBurned}</Typography>
            </CardContent>
          </Card>
          <Card elevation={2} sx={{ flex: 1 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Total Duration</Typography>
              <Typography variant="h4" fontWeight="bold">{totalDuration} min</Typography>
            </CardContent>
          </Card>
        </Stack>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontWeight="bold">Recent Workouts</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddDialogOpen(true)}
          >
            Start Workout
          </Button>
        </Box>

        {loading && workouts.length === 0 ? (
          <Box sx={{ py: 4 }}><LinearProgress /></Box>
        ) : workouts.length === 0 ? (
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <FitnessCenter sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>No workouts logged yet</Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Start your first workout to begin tracking your fitness journey
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setAddDialogOpen(true)}
              >
                Start First Workout
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Stack spacing={2}>
            {workouts.map((workout) => (
              <Card key={workout.id} elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                        <Typography variant="h6" fontWeight="bold">
                          {workout.workoutName || 'Workout'}
                        </Typography>
                        <Chip
                          label={workout.status}
                          size="small"
                          color={getStatusColor(workout.status)}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(workout.startTime).toLocaleString()}
                      </Typography>

                      <Stack direction="row" spacing={3} sx={{ mt: 2 }}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">Duration</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {workout.totalDurationMinutes || 0} min
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary">Calories</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {workout.totalCaloriesBurned || 0} kcal
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary">Exercises</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {workout.exercises?.length || 0}
                          </Typography>
                        </Box>
                      </Stack>
                    </Box>

                    <Stack direction="row" spacing={1}>
                      {workout.status === 'IN_PROGRESS' && (
                        <IconButton
                          color="success"
                          onClick={() => handleCompleteWorkout(workout.id)}
                        >
                          <Stop />
                        </IconButton>
                      )}
                      <IconButton
                        color="error"
                        onClick={() => handleDeleteWorkout(workout.id)}
                      >
                        <Delete />
                      </IconButton>
                    </Stack>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}

        <AddWorkoutDialog
          open={addDialogOpen}
          onClose={() => {
            setAddDialogOpen(false);
            dispatch(fetchWorkoutsByDate(currentDate));
          }}
          date={currentDate}
        />
      </Stack>
    </MainLayout>
  );
};

export default WorkoutsPage;
