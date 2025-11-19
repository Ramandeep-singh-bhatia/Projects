import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Chip,
  Stack,
  Menu,
  MenuItem,
  ListItemIcon,
} from '@mui/material';
import {
  MoreVert,
  Edit,
  Delete,
  Restaurant,
  LocalFireDepartment,
} from '@mui/icons-material';
import type { Meal } from '../../types/nutrition.types';

interface MealCardProps {
  meal: Meal;
  onEdit?: (meal: Meal) => void;
  onDelete?: (mealId: number) => void;
}

const MealCard: React.FC<MealCardProps> = ({ meal, onEdit, onDelete }) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    handleMenuClose();
    onEdit?.(meal);
  };

  const handleDelete = () => {
    handleMenuClose();
    onDelete?.(meal.id);
  };

  const totalCalories = meal.items.reduce(
    (sum, item) => sum + (item.foodItem.caloriesPerServing * item.servings),
    0
  );

  const totalProtein = meal.items.reduce(
    (sum, item) => sum + (item.foodItem.proteinGrams * item.servings),
    0
  );

  const totalCarbs = meal.items.reduce(
    (sum, item) => sum + (item.foodItem.carbsGrams * item.servings),
    0
  );

  const totalFat = meal.items.reduce(
    (sum, item) => sum + (item.foodItem.fatGrams * item.servings),
    0
  );

  const getMealTypeColor = (type: string) => {
    switch (type) {
      case 'BREAKFAST': return 'success';
      case 'LUNCH': return 'primary';
      case 'DINNER': return 'secondary';
      case 'SNACK': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Restaurant color="action" />
            <Box>
              <Typography variant="h6" fontWeight="bold">
                {meal.name || meal.mealType}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {new Date(meal.mealDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={meal.mealType}
              size="small"
              color={getMealTypeColor(meal.mealType)}
            />
            <IconButton size="small" onClick={handleMenuOpen}>
              <MoreVert />
            </IconButton>
          </Box>
        </Box>

        {/* Meal Items */}
        <Stack spacing={1} sx={{ mb: 2 }}>
          {meal.items.map((item) => (
            <Box
              key={item.id}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                py: 0.5,
              }}
            >
              <Typography variant="body2">
                {item.foodItem.name} × {item.servings}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {(item.foodItem.caloriesPerServing * item.servings).toFixed(0)} cal
              </Typography>
            </Box>
          ))}
        </Stack>

        {/* Nutrition Summary */}
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            p: 1.5,
            backgroundColor: 'grey.50',
            borderRadius: 1,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <LocalFireDepartment fontSize="small" color="error" />
            <Typography variant="body2" fontWeight="bold">
              {totalCalories.toFixed(0)} cal
            </Typography>
          </Box>
          <Typography variant="body2">P: {totalProtein.toFixed(0)}g</Typography>
          <Typography variant="body2">C: {totalCarbs.toFixed(0)}g</Typography>
          <Typography variant="body2">F: {totalFat.toFixed(0)}g</Typography>
        </Box>

        {meal.notes && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5, fontStyle: 'italic' }}>
            "{meal.notes}"
          </Typography>
        )}

        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleEdit}>
            <ListItemIcon>
              <Edit fontSize="small" />
            </ListItemIcon>
            Edit Meal
          </MenuItem>
          <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
            <ListItemIcon>
              <Delete fontSize="small" color="error" />
            </ListItemIcon>
            Delete Meal
          </MenuItem>
        </Menu>
      </CardContent>
    </Card>
  );
};

export default MealCard;
