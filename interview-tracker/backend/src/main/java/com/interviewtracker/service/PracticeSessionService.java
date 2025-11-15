package com.interviewtracker.service;

import com.interviewtracker.exception.ResourceNotFoundException;
import com.interviewtracker.model.PracticeSession;
import com.interviewtracker.model.Topic;
import com.interviewtracker.repository.PracticeSessionRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class PracticeSessionService {

    @Autowired
    private PracticeSessionRepository sessionRepository;

    @Autowired
    private TopicService topicService;

    public List<PracticeSession> getSessionsByTopicId(Long topicId) {
        return sessionRepository.findByTopicIdOrderBySessionDateDesc(topicId);
    }

    public PracticeSession getSessionById(Long id) {
        return sessionRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Practice session not found with id: " + id));
    }

    @Transactional
    public PracticeSession createSession(Long topicId, PracticeSession session) {
        Topic topic = topicService.getTopicById(topicId);
        session.setTopic(topic);

        // Save the session
        PracticeSession savedSession = sessionRepository.save(session);

        // Update topic's confidence and last studied date
        topicService.updateConfidence(topicId, session.getPerformanceRating());
        topicService.updateLastStudiedDate(topicId, session.getSessionDate());

        return savedSession;
    }

    @Transactional
    public PracticeSession updateSession(Long id, PracticeSession updatedSession) {
        PracticeSession existingSession = getSessionById(id);

        existingSession.setDuration(updatedSession.getDuration());
        existingSession.setPerformanceRating(updatedSession.getPerformanceRating());
        existingSession.setWhatWentWell(updatedSession.getWhatWentWell());
        existingSession.setMistakesMade(updatedSession.getMistakesMade());
        existingSession.setSessionNotes(updatedSession.getSessionNotes());
        existingSession.setSessionType(updatedSession.getSessionType());

        PracticeSession saved = sessionRepository.save(existingSession);

        // Update topic's confidence with latest performance rating
        topicService.updateConfidence(existingSession.getTopic().getId(), updatedSession.getPerformanceRating());

        return saved;
    }

    @Transactional
    public void deleteSession(Long id) {
        PracticeSession session = getSessionById(id);
        sessionRepository.delete(session);
    }

    public List<PracticeSession> getRecentSessions(int limit) {
        return sessionRepository.findRecentSessions(limit);
    }

    public List<PracticeSession> getSessionsAfter(LocalDateTime startDate) {
        return sessionRepository.findSessionsAfter(startDate);
    }

    public Long countDistinctDaysStudied(LocalDateTime startDate) {
        return sessionRepository.countDistinctDaysStudied(startDate);
    }
}
