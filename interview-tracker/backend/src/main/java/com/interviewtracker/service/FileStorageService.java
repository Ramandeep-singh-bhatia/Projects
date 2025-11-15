package com.interviewtracker.service;

import com.interviewtracker.config.FileStorageConfig;
import com.interviewtracker.exception.FileStorageException;
import com.interviewtracker.exception.ResourceNotFoundException;
import com.interviewtracker.model.FileMetadata;
import com.interviewtracker.model.Topic;
import com.interviewtracker.repository.FileMetadataRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.UUID;

@Service
public class FileStorageService {

    @Autowired
    private FileStorageConfig fileStorageConfig;

    @Autowired
    private FileMetadataRepository fileMetadataRepository;

    @Autowired
    private TopicService topicService;

    private static final List<String> ALLOWED_EXTENSIONS = List.of(
            "pdf", "docx", "doc", "txt", "md", "html",
            "png", "jpg", "jpeg", "gif", "webp"
    );

    @Transactional
    public FileMetadata uploadFile(Long topicId, MultipartFile file) {
        Topic topic = topicService.getTopicById(topicId);

        // Validate file
        if (file.isEmpty()) {
            throw new FileStorageException("Cannot upload empty file");
        }

        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename());
        String fileExtension = getFileExtension(originalFilename);

        if (!ALLOWED_EXTENSIONS.contains(fileExtension.toLowerCase())) {
            throw new FileStorageException("File type not allowed: " + fileExtension);
        }

        try {
            // Create topic-specific directory
            Path topicDir = Paths.get(fileStorageConfig.getUploadDir(), "topic-" + topicId)
                    .toAbsolutePath().normalize();
            if (!Files.exists(topicDir)) {
                Files.createDirectories(topicDir);
            }

            // Generate unique filename
            String uniqueFilename = UUID.randomUUID().toString() + "_" + originalFilename;
            Path targetLocation = topicDir.resolve(uniqueFilename);

            // Copy file to target location
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);

            // Create file metadata
            FileMetadata fileMetadata = new FileMetadata();
            fileMetadata.setTopic(topic);
            fileMetadata.setFileName(originalFilename);
            fileMetadata.setFilePath(targetLocation.toString());
            fileMetadata.setFileType(fileExtension);
            fileMetadata.setFileSize(file.getSize());

            return fileMetadataRepository.save(fileMetadata);

        } catch (IOException ex) {
            throw new FileStorageException("Could not store file " + originalFilename, ex);
        }
    }

    public List<FileMetadata> getFilesByTopicId(Long topicId) {
        return fileMetadataRepository.findByTopicIdOrderByUploadDateDesc(topicId);
    }

    public FileMetadata getFileMetadata(Long fileId) {
        return fileMetadataRepository.findById(fileId)
                .orElseThrow(() -> new ResourceNotFoundException("File not found with id: " + fileId));
    }

    public Resource loadFileAsResource(Long fileId) {
        FileMetadata fileMetadata = getFileMetadata(fileId);
        try {
            Path filePath = Paths.get(fileMetadata.getFilePath()).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists() && resource.isReadable()) {
                return resource;
            } else {
                throw new FileStorageException("File not found: " + fileMetadata.getFileName());
            }
        } catch (MalformedURLException ex) {
            throw new FileStorageException("File not found: " + fileMetadata.getFileName(), ex);
        }
    }

    @Transactional
    public void deleteFile(Long fileId) {
        FileMetadata fileMetadata = getFileMetadata(fileId);

        // Delete physical file
        try {
            Path filePath = Paths.get(fileMetadata.getFilePath());
            Files.deleteIfExists(filePath);
        } catch (IOException ex) {
            throw new FileStorageException("Could not delete file", ex);
        }

        // Delete metadata
        fileMetadataRepository.delete(fileMetadata);
    }

    public String getFileExtension(String filename) {
        if (filename == null || !filename.contains(".")) {
            return "";
        }
        return filename.substring(filename.lastIndexOf(".") + 1);
    }

    public boolean isImageFile(String fileType) {
        return List.of("png", "jpg", "jpeg", "gif", "webp").contains(fileType.toLowerCase());
    }

    public boolean isTextFile(String fileType) {
        return List.of("txt", "md", "html").contains(fileType.toLowerCase());
    }
}
