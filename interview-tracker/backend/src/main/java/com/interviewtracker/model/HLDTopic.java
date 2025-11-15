package com.interviewtracker.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Entity
@DiscriminatorValue("HLD")
@Data
@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
public class HLDTopic extends Topic {

    @Column
    private Integer pagesRead;

    @Override
    public TopicCategory getCategory() {
        return TopicCategory.HLD;
    }
}
