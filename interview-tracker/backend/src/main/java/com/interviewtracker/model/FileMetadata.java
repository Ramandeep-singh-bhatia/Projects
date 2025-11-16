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
import java.util.HashSet;
import java.util.Set;

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

    // Phase 3: Enhanced file management
    @Enumerated(EnumType.STRING)
    private FileCategory category;

    @ElementCollection
    @CollectionTable(name = "file_tags", joinColumns = @JoinColumn(name = "file_id"))
    @Column(name = "tag")
    private Set<String> tags = new HashSet<>();

    private Integer version = 1; // File version number
    private Long parentFileId; // ID of previous version (if this is a new version)
    private Integer viewCount = 0; // Track how many times file was viewed
    private LocalDateTime lastViewedDate;
}
