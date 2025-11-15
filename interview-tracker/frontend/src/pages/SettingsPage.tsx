import { useState, useEffect } from 'react';
import { settingsService, dataService } from '../services/api';
import { Settings, WeekStartDay, Theme } from '../types';

const SettingsPage = () => {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [storageInfo, setStorageInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
    loadStorageInfo();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await settingsService.get();
      setSettings(response.data);
    } catch (error) {
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStorageInfo = async () => {
    try {
      const response = await dataService.getStorageInfo();
      setStorageInfo(response.data);
    } catch (error) {
      console.error('Error loading storage info:', error);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      await settingsService.update(settings);
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await dataService.export();
      const blob = new Blob([response.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `interview-tracker-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Failed to export data');
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const merge = window.confirm('Merge with existing data? Click OK to merge, Cancel to replace all data.');

    try {
      await dataService.import(file, merge);
      alert('Data imported successfully!');
      window.location.reload();
    } catch (error) {
      console.error('Error importing data:', error);
      alert('Failed to import data');
    }
  };

  const handleReset = async () => {
    const confirmation = window.prompt(
      'This will delete ALL data and cannot be undone. Type "DELETE ALL DATA" to confirm:'
    );

    if (confirmation !== 'DELETE ALL DATA') {
      return;
    }

    try {
      await dataService.reset();
      alert('All data has been reset successfully');
      window.location.reload();
    } catch (error) {
      console.error('Error resetting data:', error);
      alert('Failed to reset data');
    }
  };

  const handleBackup = async () => {
    try {
      await dataService.backup();
      alert('Backup created successfully!');
      loadStorageInfo();
    } catch (error) {
      console.error('Error creating backup:', error);
      alert('Failed to create backup');
    }
  };

  if (loading || !settings) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      {/* Study Configuration */}
      <div className="card mb-6">
        <h2 className="text-2xl font-semibold mb-4">Study Configuration</h2>
        <div className="space-y-4">
          <div>
            <label className="label">Daily Study Hours (1-12)</label>
            <input
              type="number"
              min="1"
              max="12"
              className="input"
              value={settings.dailyStudyHours}
              onChange={(e) => setSettings({ ...settings, dailyStudyHours: parseInt(e.target.value) })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Weekly DSA Goal</label>
              <input
                type="number"
                min="0"
                className="input"
                value={settings.weeklyDsaGoal}
                onChange={(e) => setSettings({ ...settings, weeklyDsaGoal: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <label className="label">Weekly HLD Goal</label>
              <input
                type="number"
                min="0"
                className="input"
                value={settings.weeklyHldGoal}
                onChange={(e) => setSettings({ ...settings, weeklyHldGoal: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <label className="label">Weekly LLD Goal</label>
              <input
                type="number"
                min="0"
                className="input"
                value={settings.weeklyLldGoal}
                onChange={(e) => setSettings({ ...settings, weeklyLldGoal: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <label className="label">Weekly Behavioral Goal</label>
              <input
                type="number"
                min="0"
                className="input"
                value={settings.weeklyBehavioralGoal}
                onChange={(e) => setSettings({ ...settings, weeklyBehavioralGoal: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div>
            <label className="label">Week Starts On</label>
            <select
              className="input"
              value={settings.weekStartDay}
              onChange={(e) => setSettings({ ...settings, weekStartDay: e.target.value as WeekStartDay })}
            >
              <option value="MONDAY">Monday</option>
              <option value="SUNDAY">Sunday</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="btn btn-primary mt-4"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>

      {/* Data Management */}
      <div className="card mb-6">
        <h2 className="text-2xl font-semibold mb-4">Data Management</h2>

        <div className="space-y-4">
          <div className="border-b dark:border-gray-700 pb-4">
            <h3 className="font-semibold mb-2">Export Data</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Download all your data as a JSON file for backup or transfer.
            </p>
            <button onClick={handleExport} className="btn btn-primary">
              Export Data
            </button>
          </div>

          <div className="border-b dark:border-gray-700 pb-4">
            <h3 className="font-semibold mb-2">Import Data</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Upload a previously exported JSON file to restore or merge data.
            </p>
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              className="input"
            />
          </div>

          <div className="border-b dark:border-gray-700 pb-4">
            <h3 className="font-semibold mb-2">Create Backup</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Create a backup of all data in the backups directory.
            </p>
            <button onClick={handleBackup} className="btn btn-primary">
              Create Backup
            </button>
          </div>

          <div>
            <h3 className="font-semibold mb-2 text-red-600">Reset All Data</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Delete all topics, sessions, files, and reset settings. A backup will be created automatically.
            </p>
            <button onClick={handleReset} className="btn btn-danger">
              Reset All Data
            </button>
          </div>
        </div>
      </div>

      {/* Storage Info */}
      {storageInfo && (
        <div className="card">
          <h2 className="text-2xl font-semibold mb-4">About</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Version:</span>
              <span className="font-medium">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Database Location:</span>
              <span className="font-medium truncate ml-4">{storageInfo.databaseLocation}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Storage Used:</span>
              <span className="font-medium">{storageInfo.uploadStorageUsed}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Last Backup:</span>
              <span className="font-medium">{storageInfo.lastBackupDate}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
