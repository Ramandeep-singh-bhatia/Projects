import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
  Typography,
  Box,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  CircularProgress,
  InputAdornment,
} from '@mui/material';
import { Close, Add, Search, Delete } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../store';
import { createWorkout } from '../../features/workout/workoutSlice';
import workoutService from '../../api/workout.service';
import type { Exercise } from '../../types/workout.types';

interface AddWorkoutDialogProps {
  open: boolean;
  onClose: () => void;
  date: string;
}

interface SelectedExercise {
  exercise: Exercise;
  sets: number;
  reps: number;
  weight: number;
  duration: number;
  distance: number;
  notes: string;
}

const AddWorkoutDialog: React.FC<AddWorkoutDialogProps> = ({ open, onClose, date }) => {
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);
  const [workoutName, setWorkoutName] = useState('');
  const [notes, setNotes] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Exercise[]>([]);
  const [selectedExercises, setSelectedExercises] = useState<SelectedExercise[]>([]);
  const [searching, setSearching] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const results = await workoutService.searchExercises(searchQuery, 0, 10);
      setSearchResults(results.content);
    } catch (error) {
      console.error('Failed to search exercises:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleAddExercise = (exercise: Exercise) => {
    setSelectedExercises([
      ...selectedExercises,
      {
        exercise,
        sets: 3,
        reps: 10,
        weight: 0,
        duration: 0,
        distance: 0,
        notes: '',
      },
    ]);
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleRemoveExercise = (index: number) => {
    setSelectedExercises(selectedExercises.filter((_, i) => i !== index));
  };

  const handleUpdateExercise = (index: number, field: keyof SelectedExercise, value: any) => {
    const updated = [...selectedExercises];
    updated[index] = { ...updated[index], [field]: value };
    setSelectedExercises(updated);
  };

  const handleSubmit = async () => {
    if (selectedExercises.length === 0 || !workoutName || !user) return;

    setSubmitting(true);
    try {
      const workoutExercises = selectedExercises.map((item) => ({
        exerciseId: item.exercise.id,
        plannedSets: item.sets,
        plannedReps: item.reps,
        weightKg: item.weight || undefined,
        plannedDurationSeconds: item.duration ? item.duration * 60 : undefined,
      }));

      await dispatch(
        createWorkout({
          userId: user.id,
          workoutName: workoutName,
          workoutDate: date,
          startTime: new Date().toISOString(),
          notes: notes || undefined,
          exercises: workoutExercises,
        })
      ).unwrap();

      handleClose();
    } catch (error) {
      console.error('Failed to create workout:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setWorkoutName('');
    setNotes('');
    setSearchQuery('');
    setSearchResults([]);
    setSelectedExercises([]);
    onClose();
  };

  const totalCaloriesBurned = selectedExercises.reduce((sum, item) => {
    // Rough estimate: 5 calories per set, plus duration-based for cardio
    return sum + item.sets * 5 + (item.duration ? item.duration * 8 : 0);
  }, 0);

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Add Workout</Typography>
          <IconButton onClick={handleClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Stack spacing={3}>
          {/* Workout Details */}
          <TextField
            label="Workout Name"
            value={workoutName}
            onChange={(e) => setWorkoutName(e.target.value)}
            placeholder="e.g., Morning Strength Training"
            fullWidth
            required
          />

          <Divider />

          {/* Exercise Search */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Add Exercises
            </Typography>
            <Stack direction="row" spacing={1}>
              <TextField
                fullWidth
                placeholder="Search for exercises..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
              <Button
                variant="contained"
                onClick={handleSearch}
                disabled={searching || !searchQuery.trim()}
              >
                {searching ? <CircularProgress size={24} /> : 'Search'}
              </Button>
            </Stack>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <List
                sx={{
                  mt: 2,
                  maxHeight: 200,
                  overflow: 'auto',
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                }}
              >
                {searchResults.map((exercise) => (
                  <ListItem key={exercise.id} onClick={() => handleAddExercise(exercise)}>
                    <ListItemText
                      primary={exercise.name}
                      secondary={`${exercise.muscleGroup} • ${exercise.equipmentNeeded || 'No equipment'}`}
                    />
                    <ListItemSecondaryAction>
                      <IconButton edge="end" onClick={() => handleAddExercise(exercise)} size="small">
                        <Add />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </Box>

          <Divider />

          {/* Selected Exercises */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Selected Exercises ({selectedExercises.length})
            </Typography>
            {selectedExercises.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                No exercises added yet. Search and add exercises above.
              </Typography>
            ) : (
              <Stack spacing={2}>
                {selectedExercises.map((item, index) => (
                  <Box
                    key={index}
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      p: 2,
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle2">{item.exercise.name}</Typography>
                      <IconButton
                        size="small"
                        onClick={() => handleRemoveExercise(index)}
                        color="error"
                      >
                        <Delete />
                      </IconButton>
                    </Box>

                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      <TextField
                        type="number"
                        size="small"
                        label="Sets"
                        value={item.sets}
                        onChange={(e) =>
                          handleUpdateExercise(index, 'sets', parseInt(e.target.value) || 0)
                        }
                        sx={{ width: 80 }}
                        inputProps={{ min: 1 }}
                      />
                      <TextField
                        type="number"
                        size="small"
                        label="Reps"
                        value={item.reps}
                        onChange={(e) =>
                          handleUpdateExercise(index, 'reps', parseInt(e.target.value) || 0)
                        }
                        sx={{ width: 80 }}
                        inputProps={{ min: 1 }}
                      />
                      <TextField
                        type="number"
                        size="small"
                        label="Weight (kg)"
                        value={item.weight || ''}
                        onChange={(e) =>
                          handleUpdateExercise(index, 'weight', parseFloat(e.target.value) || 0)
                        }
                        sx={{ width: 100 }}
                        inputProps={{ min: 0, step: 0.5 }}
                      />
                      <TextField
                        type="number"
                        size="small"
                        label="Duration (min)"
                        value={item.duration || ''}
                        onChange={(e) =>
                          handleUpdateExercise(index, 'duration', parseInt(e.target.value) || 0)
                        }
                        sx={{ width: 120 }}
                        inputProps={{ min: 0 }}
                      />
                      <TextField
                        type="number"
                        size="small"
                        label="Distance (km)"
                        value={item.distance || ''}
                        onChange={(e) =>
                          handleUpdateExercise(index, 'distance', parseFloat(e.target.value) || 0)
                        }
                        sx={{ width: 120 }}
                        inputProps={{ min: 0, step: 0.1 }}
                      />
                    </Stack>

                    <TextField
                      size="small"
                      label="Notes"
                      value={item.notes}
                      onChange={(e) => handleUpdateExercise(index, 'notes', e.target.value)}
                      fullWidth
                      sx={{ mt: 1 }}
                      placeholder="Add notes for this exercise..."
                    />
                  </Box>
                ))}
              </Stack>
            )}

            {selectedExercises.length > 0 && (
              <Box sx={{ mt: 2, p: 2, backgroundColor: 'primary.50', borderRadius: 1 }}>
                <Typography variant="subtitle2">
                  Estimated Calories Burned: ~{totalCaloriesBurned.toFixed(0)} cal
                </Typography>
              </Box>
            )}
          </Box>

          {/* Notes */}
          <TextField
            label="Workout Notes (Optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            multiline
            rows={2}
            placeholder="Add any notes about this workout..."
            fullWidth
          />
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={submitting}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={selectedExercises.length === 0 || !workoutName || submitting}
        >
          {submitting ? <CircularProgress size={24} /> : 'Add Workout'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddWorkoutDialog;
