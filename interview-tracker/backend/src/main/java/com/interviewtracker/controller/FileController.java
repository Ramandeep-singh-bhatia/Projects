package com.interviewtracker.controller;

import com.interviewtracker.model.FileMetadata;
import com.interviewtracker.service.FileStorageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

@RestController
@RequestMapping("/api/files")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class FileController {

    @Autowired
    private FileStorageService fileStorageService;

    @PostMapping("/upload/{topicId}")
    public ResponseEntity<FileMetadata> uploadFile(
            @PathVariable Long topicId,
            @RequestParam("file") MultipartFile file) {

        FileMetadata fileMetadata = fileStorageService.uploadFile(topicId, file);
        return new ResponseEntity<>(fileMetadata, HttpStatus.CREATED);
    }

    @GetMapping("/topic/{topicId}")
    public ResponseEntity<List<FileMetadata>> getFilesByTopicId(@PathVariable Long topicId) {
        List<FileMetadata> files = fileStorageService.getFilesByTopicId(topicId);
        return ResponseEntity.ok(files);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Resource> downloadFile(@PathVariable Long id) {
        FileMetadata fileMetadata = fileStorageService.getFileMetadata(id);
        Resource resource = fileStorageService.loadFileAsResource(id);

        String contentType = "application/octet-stream";
        try {
            contentType = Files.probeContentType(Paths.get(fileMetadata.getFilePath()));
            if (contentType == null) {
                contentType = "application/octet-stream";
            }
        } catch (IOException e) {
            // Use default content type
        }

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + fileMetadata.getFileName() + "\"")
                .body(resource);
    }

    @GetMapping("/{id}/preview")
    public ResponseEntity<?> previewFile(@PathVariable Long id) {
        FileMetadata fileMetadata = fileStorageService.getFileMetadata(id);
        Resource resource = fileStorageService.loadFileAsResource(id);

        // For images, return the image directly
        if (fileStorageService.isImageFile(fileMetadata.getFileType())) {
            String contentType = "image/" + fileMetadata.getFileType();
            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType(contentType))
                    .body(resource);
        }

        // For text files, return content as text
        if (fileStorageService.isTextFile(fileMetadata.getFileType())) {
            try {
                String content = Files.readString(Paths.get(fileMetadata.getFilePath()));
                return ResponseEntity.ok()
                        .contentType(MediaType.TEXT_PLAIN)
                        .body(content);
            } catch (IOException e) {
                return ResponseEntity.internalServerError()
                        .body("Could not read file content");
            }
        }

        // For other files, return metadata only
        return ResponseEntity.ok(fileMetadata);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteFile(@PathVariable Long id) {
        fileStorageService.deleteFile(id);
        return ResponseEntity.noContent().build();
    }
}
