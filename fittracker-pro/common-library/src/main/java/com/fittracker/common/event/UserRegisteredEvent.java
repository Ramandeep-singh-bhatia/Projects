package com.fittracker.common.event;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserRegisteredEvent implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long userId;
    private String email;
    private String firstName;
    private String lastName;
    private LocalDateTime registeredAt;
    private String eventId;
    private LocalDateTime eventTimestamp;

    public static UserRegisteredEvent create(Long userId, String email, String firstName, String lastName) {
        return UserRegisteredEvent.builder()
                .userId(userId)
                .email(email)
                .firstName(firstName)
                .lastName(lastName)
                .registeredAt(LocalDateTime.now())
                .eventId(java.util.UUID.randomUUID().toString())
                .eventTimestamp(LocalDateTime.now())
                .build();
    }
}
