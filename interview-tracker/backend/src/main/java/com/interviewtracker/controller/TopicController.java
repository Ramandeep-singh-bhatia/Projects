package com.interviewtracker.controller;

import com.interviewtracker.model.*;
import com.interviewtracker.service.TopicService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/topics")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class TopicController {

    @Autowired
    private TopicService topicService;

    @GetMapping("/{category}")
    public ResponseEntity<List<Topic>> getAllTopicsByCategory(@PathVariable String category) {
        TopicCategory topicCategory = TopicCategory.valueOf(category.toUpperCase());
        List<Topic> topics = topicService.getAllTopicsByCategory(topicCategory);
        return ResponseEntity.ok(topics);
    }

    @GetMapping("/{category}/{id}")
    public ResponseEntity<Topic> getTopicById(@PathVariable Long id) {
        Topic topic = topicService.getTopicById(id);
        return ResponseEntity.ok(topic);
    }

    @PostMapping("/{category}")
    public ResponseEntity<Topic> createTopic(
            @PathVariable String category,
            @Valid @RequestBody Topic topic) {

        TopicCategory topicCategory = TopicCategory.valueOf(category.toUpperCase());
        Topic createdTopic = topicService.createTopic(topicCategory, topic);
        return new ResponseEntity<>(createdTopic, HttpStatus.CREATED);
    }

    @PutMapping("/{category}/{id}")
    public ResponseEntity<Topic> updateTopic(
            @PathVariable Long id,
            @Valid @RequestBody Topic topic) {

        Topic updatedTopic = topicService.updateTopic(id, topic);
        return ResponseEntity.ok(updatedTopic);
    }

    @DeleteMapping("/{category}/{id}")
    public ResponseEntity<Void> deleteTopic(@PathVariable Long id) {
        topicService.deleteTopic(id);
        return ResponseEntity.noContent().build();
    }
}
