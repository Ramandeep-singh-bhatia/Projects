package com.interviewtracker.model;

import jakarta.persistence.*;
import lombok.Data;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "voice_notes")
@Data
@EntityListeners(AuditingEntityListener.class)
public class VoiceNote {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id")
    private Topic topic; // Optional link to topic

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    private PracticeSession session; // Optional link to session

    private String audioFilePath; // ~/interview-tracker/audio/
    private Integer duration; // seconds
    private Long fileSize; // bytes

    @Column(length = 10000)
    private String transcription; // Speech-to-text result

    private Boolean transcribed = false;

    @CreatedDate
    private LocalDateTime recordedDate;

    private String title; // Optional user-provided title

    @Column(length = 2000)
    private String summary; // Optional summary

    @ElementCollection
    @CollectionTable(name = "voice_note_tags", joinColumns = @JoinColumn(name = "voice_note_id"))
    @Column(name = "tag")
    private Set<String> tags = new HashSet<>();
}
