package com.interviewtracker.repository;

import com.interviewtracker.model.Topic;
import com.interviewtracker.model.TopicDependency;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TopicDependencyRepository extends JpaRepository<TopicDependency, Long> {

    List<TopicDependency> findByTopic(Topic topic);

    List<TopicDependency> findByPrerequisite(Topic prerequisite);

    Optional<TopicDependency> findByTopicAndPrerequisite(Topic topic, Topic prerequisite);

    @Query("SELECT td FROM TopicDependency td WHERE td.topic.id = :topicId")
    List<TopicDependency> findPrerequisitesForTopic(@Param("topicId") Long topicId);

    @Query("SELECT td FROM TopicDependency td WHERE td.prerequisite.id = :topicId")
    List<TopicDependency> findDependentsOfTopic(@Param("topicId") Long topicId);
}
