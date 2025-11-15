package com.interviewtracker.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Entity
@DiscriminatorValue("DSA")
@Data
@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
public class DSATopic extends Topic {

    @NotNull(message = "Difficulty level is required for DSA topics")
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private DifficultyLevel difficulty;

    @Override
    public TopicCategory getCategory() {
        return TopicCategory.DSA;
    }
}
