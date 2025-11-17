package com.fittracker.analytics.controller;

import com.fittracker.analytics.entity.MonthlyReport;
import com.fittracker.analytics.entity.WeeklyReport;
import com.fittracker.analytics.service.ReportService;
import com.fittracker.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/analytics/reports")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @PostMapping("/weekly/{userId}")
    public ResponseEntity<ApiResponse<WeeklyReport>> generateWeeklyReport(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate weekStartDate) {
        log.info("Generate weekly report for user {} - week starting {}", userId, weekStartDate);
        WeeklyReport report = reportService.generateWeeklyReport(userId, weekStartDate);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Weekly report generated successfully", report));
    }

    @PostMapping("/monthly/{userId}")
    public ResponseEntity<ApiResponse<MonthlyReport>> generateMonthlyReport(
            @PathVariable Long userId,
            @RequestParam int year,
            @RequestParam int month) {
        log.info("Generate monthly report for user {} - {}/{}", userId, year, month);
        MonthlyReport report = reportService.generateMonthlyReport(userId, year, month);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Monthly report generated successfully", report));
    }

    @GetMapping("/weekly/{userId}")
    public ResponseEntity<ApiResponse<WeeklyReport>> getWeeklyReport(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate weekStartDate) {
        log.info("Get weekly report for user {} - week starting {}", userId, weekStartDate);
        WeeklyReport report = reportService.getWeeklyReport(userId, weekStartDate);
        if (report == null) {
            return ResponseEntity.ok(ApiResponse.success("No report found for this week", null));
        }
        return ResponseEntity.ok(ApiResponse.success(report));
    }

    @GetMapping("/monthly/{userId}")
    public ResponseEntity<ApiResponse<MonthlyReport>> getMonthlyReport(
            @PathVariable Long userId,
            @RequestParam int year,
            @RequestParam int month) {
        log.info("Get monthly report for user {} - {}/{}", userId, year, month);
        MonthlyReport report = reportService.getMonthlyReport(userId, year, month);
        if (report == null) {
            return ResponseEntity.ok(ApiResponse.success("No report found for this month", null));
        }
        return ResponseEntity.ok(ApiResponse.success(report));
    }

    @GetMapping("/weekly/{userId}/all")
    public ResponseEntity<ApiResponse<List<WeeklyReport>>> getAllWeeklyReports(@PathVariable Long userId) {
        log.info("Get all weekly reports for user {}", userId);
        List<WeeklyReport> reports = reportService.getAllWeeklyReports(userId);
        return ResponseEntity.ok(ApiResponse.success(reports));
    }

    @GetMapping("/monthly/{userId}/all")
    public ResponseEntity<ApiResponse<List<MonthlyReport>>> getAllMonthlyReports(@PathVariable Long userId) {
        log.info("Get all monthly reports for user {}", userId);
        List<MonthlyReport> reports = reportService.getAllMonthlyReports(userId);
        return ResponseEntity.ok(ApiResponse.success(reports));
    }

    @GetMapping("/weekly/{userId}/recent")
    public ResponseEntity<ApiResponse<List<WeeklyReport>>> getRecentWeeklyReports(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "4") int weeks) {
        log.info("Get last {} weeks of reports for user {}", weeks, userId);
        List<WeeklyReport> reports = reportService.getRecentWeeklyReports(userId, weeks);
        return ResponseEntity.ok(ApiResponse.success(reports));
    }
}
