package com.interviewtracker.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Entity
@DiscriminatorValue("LLD")
@Data
@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
public class LLDTopic extends Topic {

    @Override
    public TopicCategory getCategory() {
        return TopicCategory.LLD;
    }
}
