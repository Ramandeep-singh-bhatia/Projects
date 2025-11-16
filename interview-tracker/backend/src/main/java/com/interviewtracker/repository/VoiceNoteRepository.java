package com.interviewtracker.repository;

import com.interviewtracker.model.Topic;
import com.interviewtracker.model.VoiceNote;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface VoiceNoteRepository extends JpaRepository<VoiceNote, Long> {

    List<VoiceNote> findByTopicOrderByRecordedDateDesc(Topic topic);

    List<VoiceNote> findTop10ByOrderByRecordedDateDesc();

    List<VoiceNote> findByTranscribedTrue();

    @Query("SELECT v FROM VoiceNote v WHERE v.transcribed = true AND " +
           "(LOWER(v.transcription) LIKE LOWER(CONCAT('%', :searchTerm, '%')) " +
           "OR LOWER(v.title) LIKE LOWER(CONCAT('%', :searchTerm, '%')))")
    List<VoiceNote> searchByTranscription(@Param("searchTerm") String searchTerm);

    @Query("SELECT SUM(v.duration) FROM VoiceNote v")
    Long getTotalDuration();

    @Query("SELECT SUM(v.fileSize) FROM VoiceNote v")
    Long getTotalFileSize();
}
