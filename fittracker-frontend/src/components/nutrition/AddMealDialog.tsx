import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
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
import { useAppDispatch } from '../../store';
import { createMeal } from '../../features/nutrition/nutritionSlice';
import nutritionService from '../../api/nutrition.service';
import { MealType } from '../../types/common.types';
import type { FoodItem } from '../../types/nutrition.types';

interface AddMealDialogProps {
  open: boolean;
  onClose: () => void;
  date: string;
}

interface SelectedFood {
  foodItem: FoodItem;
  servings: number;
}

const AddMealDialog: React.FC<AddMealDialogProps> = ({ open, onClose, date }) => {
  const dispatch = useAppDispatch();
  const [mealName, setMealName] = useState('');
  const [mealType, setMealType] = useState<string>(MealType.BREAKFAST);
  const [notes, setNotes] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<FoodItem[]>([]);
  const [selectedFoods, setSelectedFoods] = useState<SelectedFood[]>([]);
  const [searching, setSearching] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const results = await nutritionService.searchFoodItems(searchQuery, 0, 10);
      setSearchResults(results.content);
    } catch (error) {
      console.error('Failed to search foods:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleAddFood = (food: FoodItem) => {
    setSelectedFoods([...selectedFoods, { foodItem: food, servings: 1 }]);
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleRemoveFood = (index: number) => {
    setSelectedFoods(selectedFoods.filter((_, i) => i !== index));
  };

  const handleUpdateServings = (index: number, servings: number) => {
    const updated = [...selectedFoods];
    updated[index].servings = servings;
    setSelectedFoods(updated);
  };

  const handleSubmit = async () => {
    if (selectedFoods.length === 0) return;

    setSubmitting(true);
    try {
      const mealItems = selectedFoods.map(item => ({
        foodItemId: item.foodItem.id,
        servings: item.servings,
      }));

      await dispatch(createMeal({
        name: mealName || undefined,
        mealType: mealType as any,
        mealDate: `${date}T12:00:00`,
        notes: notes || undefined,
        mealItems,
      })).unwrap();

      handleClose();
    } catch (error) {
      console.error('Failed to create meal:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setMealName('');
    setMealType(MealType.BREAKFAST);
    setNotes('');
    setSearchQuery('');
    setSearchResults([]);
    setSelectedFoods([]);
    onClose();
  };

  const totalCalories = selectedFoods.reduce(
    (sum, item) => sum + (item.foodItem.caloriesPerServing * item.servings),
    0
  );

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Add Meal</Typography>
          <IconButton onClick={handleClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Stack spacing={3}>
          {/* Meal Details */}
          <Stack spacing={2}>
            <TextField
              label="Meal Name (Optional)"
              value={mealName}
              onChange={(e) => setMealName(e.target.value)}
              placeholder="e.g., Breakfast at Home"
              fullWidth
            />

            <TextField
              select
              label="Meal Type"
              value={mealType}
              onChange={(e) => setMealType(e.target.value)}
              fullWidth
            >
              <MenuItem value={MealType.BREAKFAST}>Breakfast</MenuItem>
              <MenuItem value={MealType.LUNCH}>Lunch</MenuItem>
              <MenuItem value={MealType.DINNER}>Dinner</MenuItem>
              <MenuItem value={MealType.SNACK}>Snack</MenuItem>
            </TextField>
          </Stack>

          <Divider />

          {/* Food Search */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Add Foods
            </Typography>
            <Stack direction="row" spacing={1}>
              <TextField
                fullWidth
                placeholder="Search for foods..."
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
              <List sx={{ mt: 2, maxHeight: 200, overflow: 'auto', border: 1, borderColor: 'divider', borderRadius: 1 }}>
                {searchResults.map((food) => (
                  <ListItem
                    key={food.id}
                    onClick={() => handleAddFood(food)}
                  >
                    <ListItemText
                      primary={food.name}
                      secondary={`${food.caloriesPerServing} cal per ${food.servingSize} ${food.servingUnit}`}
                    />
                    <ListItemSecondaryAction>
                      <IconButton edge="end" onClick={() => handleAddFood(food)} size="small">
                        <Add />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </Box>

          <Divider />

          {/* Selected Foods */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Selected Foods ({selectedFoods.length})
            </Typography>
            {selectedFoods.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                No foods added yet. Search and add foods above.
              </Typography>
            ) : (
              <List>
                {selectedFoods.map((item, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                    }}
                  >
                    <ListItemText
                      primary={item.foodItem.name}
                      secondary={`${item.foodItem.caloriesPerServing} cal × ${item.servings} = ${(item.foodItem.caloriesPerServing * item.servings).toFixed(0)} cal`}
                    />
                    <TextField
                      type="number"
                      size="small"
                      label="Servings"
                      value={item.servings}
                      onChange={(e) => handleUpdateServings(index, parseFloat(e.target.value) || 1)}
                      sx={{ width: 100, mr: 1 }}
                      inputProps={{ min: 0.1, step: 0.5 }}
                    />
                    <IconButton edge="end" onClick={() => handleRemoveFood(index)} color="error">
                      <Delete />
                    </IconButton>
                  </ListItem>
                ))}
              </List>
            )}

            {selectedFoods.length > 0 && (
              <Box sx={{ mt: 2, p: 2, backgroundColor: 'primary.50', borderRadius: 1 }}>
                <Typography variant="subtitle2">
                  Total: {totalCalories.toFixed(0)} calories
                </Typography>
              </Box>
            )}
          </Box>

          {/* Notes */}
          <TextField
            label="Notes (Optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            multiline
            rows={2}
            placeholder="Add any notes about this meal..."
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
          disabled={selectedFoods.length === 0 || submitting}
        >
          {submitting ? <CircularProgress size={24} /> : 'Add Meal'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddMealDialog;
