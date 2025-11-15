package com.interviewtracker.dto;

import com.interviewtracker.model.DifficultyLevel;
import com.interviewtracker.model.TopicCategory;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DashboardSuggestionDTO {
    private Long topicId;
    private String topic;
    private String subtopic;
    private TopicCategory category;
    private Integer confidence;
    private Long daysSinceLastStudied;
    private Integer estimatedTime; // in minutes
    private DifficultyLevel difficulty; // for DSA only
    private Double priorityScore;
}
