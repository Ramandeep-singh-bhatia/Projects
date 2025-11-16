import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import DashboardPage from './pages/DashboardPage';
import DSAPage from './pages/DSAPage';
import HLDPage from './pages/HLDPage';
import LLDPage from './pages/LLDPage';
import BehavioralPage from './pages/BehavioralPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import StudyPlanPage from './pages/StudyPlanPage';
import MockInterviewPage from './pages/MockInterviewPage';
import FlashcardsPage from './pages/FlashcardsPage';
import FlashcardReviewPage from './pages/FlashcardReviewPage';
import VoiceNotesPage from './pages/VoiceNotesPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="dsa" element={<DSAPage />} />
          <Route path="hld" element={<HLDPage />} />
          <Route path="lld" element={<LLDPage />} />
          <Route path="behavioral" element={<BehavioralPage />} />
          <Route path="study-plan" element={<StudyPlanPage />} />
          <Route path="mock-interview" element={<MockInterviewPage />} />
          <Route path="flashcards" element={<FlashcardsPage />} />
          <Route path="flashcards/review" element={<FlashcardReviewPage />} />
          <Route path="voice-notes" element={<VoiceNotesPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
