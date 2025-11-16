package com.interviewtracker.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "topic_dependencies_v2")
@Data
@NoArgsConstructor
public class TopicDependency {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    private Topic topic;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "prerequisite_id", nullable = false)
    private Topic prerequisite;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private DependencyStrength strength = DependencyStrength.MEDIUM;

    public TopicDependency(Topic topic, Topic prerequisite, DependencyStrength strength) {
        this.topic = topic;
        this.prerequisite = prerequisite;
        this.strength = strength;
    }
}
