package com.interviewtracker.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

import jakarta.annotation.PostConstruct;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Configuration
public class FileStorageConfig {

    @Value("${file.upload-dir}")
    private String uploadDir;

    @Value("${file.backup-dir}")
    private String backupDir;

    @PostConstruct
    public void init() {
        try {
            Path uploadPath = Paths.get(uploadDir).toAbsolutePath().normalize();
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
                System.out.println("Created upload directory: " + uploadPath);
            }

            Path backupPath = Paths.get(backupDir).toAbsolutePath().normalize();
            if (!Files.exists(backupPath)) {
                Files.createDirectories(backupPath);
                System.out.println("Created backup directory: " + backupPath);
            }
        } catch (Exception ex) {
            throw new RuntimeException("Could not create upload/backup directories!", ex);
        }
    }

    public String getUploadDir() {
        return uploadDir;
    }

    public String getBackupDir() {
        return backupDir;
    }
}
