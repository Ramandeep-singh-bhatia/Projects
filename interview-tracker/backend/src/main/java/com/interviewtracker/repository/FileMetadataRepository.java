package com.interviewtracker.repository;

import com.interviewtracker.model.FileMetadata;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FileMetadataRepository extends JpaRepository<FileMetadata, Long> {

    List<FileMetadata> findByTopicIdOrderByUploadDateDesc(Long topicId);

    void deleteByTopicId(Long topicId);
}
