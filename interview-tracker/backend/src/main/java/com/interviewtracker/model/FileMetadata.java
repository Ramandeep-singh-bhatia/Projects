package com.interviewtracker.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "file_metadata")
@EntityListeners(AuditingEntityListener.class)
@Data
@NoArgsConstructor
public class FileMetadata {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    @JsonBackReference
    private Topic topic;

    @NotBlank(message = "File name is required")
    @Column(nullable = false, length = 500)
    private String fileName;

    @NotBlank(message = "File path is required")
    @Column(nullable = false, length = 1000)
    private String filePath;

    @NotBlank(message = "File type is required")
    @Column(nullable = false, length = 100)
    private String fileType;

    @NotNull(message = "File size is required")
    @Column(nullable = false)
    private Long fileSize;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime uploadDate;
}
