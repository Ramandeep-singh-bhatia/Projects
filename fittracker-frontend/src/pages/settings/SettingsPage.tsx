import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  Switch,
  FormControlLabel,
  Divider,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
} from '@mui/material';
import { Save, Notifications, Palette, Language } from '@mui/icons-material';
import MainLayout from '../../components/layout/MainLayout';

const SettingsPage: React.FC = () => {
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    workoutReminders: true,
    mealReminders: true,
    weeklyReport: true,
  });

  const [preferences, setPreferences] = useState({
    theme: 'light',
    language: 'en',
    dateFormat: 'MM/DD/YYYY',
    weightUnit: 'kg',
    distanceUnit: 'km',
  });

  const [saved, setSaved] = useState(false);

  const handleNotificationChange = (key: string) => {
    setNotifications((prev) => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev],
    }));
  };

  const handlePreferenceChange = (key: string, value: string) => {
    setPreferences((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = () => {
    // Save settings to local storage or API
    localStorage.setItem('appSettings', JSON.stringify({ notifications, preferences }));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <MainLayout>
      <Stack spacing={4}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Settings
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Customize your FitTracker experience
          </Typography>
        </Box>

        {saved && (
          <Alert severity="success" onClose={() => setSaved(false)}>
            Settings saved successfully!
          </Alert>
        )}

        {/* Notifications */}
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <Notifications color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Notifications
              </Typography>
            </Box>

            <Stack spacing={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.email}
                    onChange={() => handleNotificationChange('email')}
                  />
                }
                label="Email Notifications"
              />
              <Typography variant="body2" color="text.secondary" sx={{ pl: 7, mt: -1 }}>
                Receive updates and notifications via email
              </Typography>

              <Divider />

              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.push}
                    onChange={() => handleNotificationChange('push')}
                  />
                }
                label="Push Notifications"
              />
              <Typography variant="body2" color="text.secondary" sx={{ pl: 7, mt: -1 }}>
                Get real-time notifications on your device
              </Typography>

              <Divider />

              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.workoutReminders}
                    onChange={() => handleNotificationChange('workoutReminders')}
                  />
                }
                label="Workout Reminders"
              />
              <Typography variant="body2" color="text.secondary" sx={{ pl: 7, mt: -1 }}>
                Remind me to complete my daily workout
              </Typography>

              <Divider />

              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.mealReminders}
                    onChange={() => handleNotificationChange('mealReminders')}
                  />
                }
                label="Meal Logging Reminders"
              />
              <Typography variant="body2" color="text.secondary" sx={{ pl: 7, mt: -1 }}>
                Remind me to log my meals
              </Typography>

              <Divider />

              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.weeklyReport}
                    onChange={() => handleNotificationChange('weeklyReport')}
                  />
                }
                label="Weekly Progress Reports"
              />
              <Typography variant="body2" color="text.secondary" sx={{ pl: 7, mt: -1 }}>
                Receive weekly summary of your progress
              </Typography>
            </Stack>
          </CardContent>
        </Card>

        {/* Preferences */}
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <Palette color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Preferences
              </Typography>
            </Box>

            <Stack spacing={3}>
              <FormControl fullWidth>
                <InputLabel>Theme</InputLabel>
                <Select
                  value={preferences.theme}
                  label="Theme"
                  onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="auto">Auto (System)</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select
                  value={preferences.language}
                  label="Language"
                  onChange={(e) => handlePreferenceChange('language', e.target.value)}
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Spanish</MenuItem>
                  <MenuItem value="fr">French</MenuItem>
                  <MenuItem value="de">German</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Date Format</InputLabel>
                <Select
                  value={preferences.dateFormat}
                  label="Date Format"
                  onChange={(e) => handlePreferenceChange('dateFormat', e.target.value)}
                >
                  <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                  <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                  <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Weight Unit</InputLabel>
                <Select
                  value={preferences.weightUnit}
                  label="Weight Unit"
                  onChange={(e) => handlePreferenceChange('weightUnit', e.target.value)}
                >
                  <MenuItem value="kg">Kilograms (kg)</MenuItem>
                  <MenuItem value="lb">Pounds (lb)</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Distance Unit</InputLabel>
                <Select
                  value={preferences.distanceUnit}
                  label="Distance Unit"
                  onChange={(e) => handlePreferenceChange('distanceUnit', e.target.value)}
                >
                  <MenuItem value="km">Kilometers (km)</MenuItem>
                  <MenuItem value="mi">Miles (mi)</MenuItem>
                </Select>
              </FormControl>
            </Stack>
          </CardContent>
        </Card>

        {/* Data & Privacy */}
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <Language color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Data & Privacy
              </Typography>
            </Box>

            <Stack spacing={2}>
              <Box>
                <Typography variant="body1" fontWeight="medium" gutterBottom>
                  Export Your Data
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Download all your data in JSON format
                </Typography>
                <Button variant="outlined" size="small">
                  Export Data
                </Button>
              </Box>

              <Divider />

              <Box>
                <Typography variant="body1" fontWeight="medium" gutterBottom>
                  Delete Account
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Permanently delete your account and all associated data
                </Typography>
                <Button variant="outlined" color="error" size="small">
                  Delete Account
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        {/* Save Button */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button variant="outlined" size="large">
            Cancel
          </Button>
          <Button variant="contained" size="large" startIcon={<Save />} onClick={handleSave}>
            Save Settings
          </Button>
        </Box>

        {/* About */}
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              About FitTracker Pro
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Version 1.0.0
            </Typography>
            <Typography variant="body2" color="text.secondary">
              FitTracker Pro is your comprehensive fitness tracking solution. Track workouts,
              nutrition, and analyze your progress all in one place.
            </Typography>
          </CardContent>
        </Card>
      </Stack>
    </MainLayout>
  );
};

export default SettingsPage;
