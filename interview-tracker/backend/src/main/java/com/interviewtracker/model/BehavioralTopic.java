package com.interviewtracker.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Entity
@DiscriminatorValue("BEHAVIORAL")
@Data
@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
public class BehavioralTopic extends Topic {

    @NotBlank(message = "Question category is required for behavioral topics")
    @Column(nullable = false, length = 200)
    private String questionCategory;

    @Override
    public TopicCategory getCategory() {
        return TopicCategory.BEHAVIORAL;
    }
}
