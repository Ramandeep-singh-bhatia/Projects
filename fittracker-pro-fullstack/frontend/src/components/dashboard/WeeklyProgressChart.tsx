import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface WeeklyProgressChartProps {
  data?: Array<{
    day: string;
    calories: number;
    burned: number;
  }>;
}

const defaultData = [
  { day: 'Mon', calories: 2100, burned: 450 },
  { day: 'Tue', calories: 2250, burned: 520 },
  { day: 'Wed', calories: 1950, burned: 380 },
  { day: 'Thu', calories: 2300, burned: 600 },
  { day: 'Fri', calories: 2150, burned: 480 },
  { day: 'Sat', calories: 2400, burned: 550 },
  { day: 'Sun', calories: 2000, burned: 420 },
];

const WeeklyProgressChart: React.FC<WeeklyProgressChartProps> = ({ data = defaultData }) => {
  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          Weekly Calorie Overview
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Calories consumed vs calories burned
        </Typography>

        <Box sx={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="calories"
                stroke="#667eea"
                strokeWidth={2}
                name="Calories Consumed"
                dot={{ fill: '#667eea', r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="burned"
                stroke="#764ba2"
                strokeWidth={2}
                name="Calories Burned"
                dot={{ fill: '#764ba2', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

export default WeeklyProgressChart;
