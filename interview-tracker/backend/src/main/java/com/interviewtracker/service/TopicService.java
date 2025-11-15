package com.interviewtracker.service;

import com.interviewtracker.exception.ResourceNotFoundException;
import com.interviewtracker.model.*;
import com.interviewtracker.repository.FileMetadataRepository;
import com.interviewtracker.repository.TopicRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.File;
import java.time.LocalDateTime;
import java.util.List;

@Service
public class TopicService {

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private FileMetadataRepository fileMetadataRepository;

    public List<Topic> getAllTopicsByCategory(TopicCategory category) {
        Class<? extends Topic> topicClass = getTopicClass(category);
        return topicRepository.findByType(topicClass);
    }

    public Topic getTopicById(Long id) {
        return topicRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Topic not found with id: " + id));
    }

    @Transactional
    public Topic createTopic(TopicCategory category, Topic topic) {
        validateTopicCategory(category, topic);
        return topicRepository.save(topic);
    }

    @Transactional
    public Topic updateTopic(Long id, Topic updatedTopic) {
        Topic existingTopic = getTopicById(id);

        // Update common fields
        existingTopic.setTopic(updatedTopic.getTopic());
        existingTopic.setSubtopic(updatedTopic.getSubtopic());
        existingTopic.setConfidence(updatedTopic.getConfidence());
        existingTopic.setSourceUrl(updatedTopic.getSourceUrl());
        existingTopic.setNotes(updatedTopic.getNotes());
        existingTopic.setThingsToRemember(updatedTopic.getThingsToRemember());

        // Update category-specific fields
        if (existingTopic instanceof DSATopic && updatedTopic instanceof DSATopic) {
            ((DSATopic) existingTopic).setDifficulty(((DSATopic) updatedTopic).getDifficulty());
        } else if (existingTopic instanceof HLDTopic && updatedTopic instanceof HLDTopic) {
            ((HLDTopic) existingTopic).setPagesRead(((HLDTopic) updatedTopic).getPagesRead());
        } else if (existingTopic instanceof BehavioralTopic && updatedTopic instanceof BehavioralTopic) {
            ((BehavioralTopic) existingTopic).setQuestionCategory(((BehavioralTopic) updatedTopic).getQuestionCategory());
        }

        return topicRepository.save(existingTopic);
    }

    @Transactional
    public void deleteTopic(Long id) {
        Topic topic = getTopicById(id);

        // Delete associated files from file system
        List<FileMetadata> files = fileMetadataRepository.findByTopicIdOrderByUploadDateDesc(id);
        for (FileMetadata fileMetadata : files) {
            File file = new File(fileMetadata.getFilePath());
            if (file.exists()) {
                file.delete();
            }
        }

        // Delete topic (cascade will delete sessions and file metadata)
        topicRepository.delete(topic);
    }

    @Transactional
    public void updateLastStudiedDate(Long topicId, LocalDateTime date) {
        Topic topic = getTopicById(topicId);
        topic.setLastStudiedDate(date);
        topicRepository.save(topic);
    }

    @Transactional
    public void updateConfidence(Long topicId, Integer confidence) {
        Topic topic = getTopicById(topicId);
        topic.setConfidence(confidence);
        topicRepository.save(topic);
    }

    public List<Topic> getTopicsStudiedThisWeek(LocalDateTime weekStart) {
        return topicRepository.findTopicsStudiedAfter(weekStart);
    }

    public List<Topic> getTopicsByCategoryStudiedThisWeek(TopicCategory category, LocalDateTime weekStart) {
        Class<? extends Topic> topicClass = getTopicClass(category);
        return topicRepository.findByTypeAndLastStudiedAfter(topicClass, weekStart);
    }

    private Class<? extends Topic> getTopicClass(TopicCategory category) {
        return switch (category) {
            case DSA -> DSATopic.class;
            case HLD -> HLDTopic.class;
            case LLD -> LLDTopic.class;
            case BEHAVIORAL -> BehavioralTopic.class;
        };
    }

    private void validateTopicCategory(TopicCategory category, Topic topic) {
        boolean valid = switch (category) {
            case DSA -> topic instanceof DSATopic;
            case HLD -> topic instanceof HLDTopic;
            case LLD -> topic instanceof LLDTopic;
            case BEHAVIORAL -> topic instanceof BehavioralTopic;
        };

        if (!valid) {
            throw new IllegalArgumentException("Topic type does not match category: " + category);
        }
    }
}
