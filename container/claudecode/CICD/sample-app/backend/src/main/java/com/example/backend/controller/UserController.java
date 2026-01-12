package com.example.backend.controller;

import com.example.backend.service.UserService;
import com.example.common.dto.UserDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;

/**
 * User REST Controller
 * ユーザー管理REST API
 */
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class UserController {

    private final UserService userService;

    /**
     * 全ユーザー一覧取得
     * GET /api/users
     */
    @GetMapping
    public ResponseEntity<List<UserDto>> getAllUsers() {
        log.debug("全ユーザー一覧取得API呼び出し");
        List<UserDto> users = userService.findAll();
        return ResponseEntity.ok(users);
    }

    /**
     * ユーザーID指定取得
     * GET /api/users/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUserById(@PathVariable Long id) {
        log.debug("ユーザー取得API呼び出し: ID={}", id);
        UserDto user = userService.findById(id);
        return ResponseEntity.ok(user);
    }

    /**
     * 部門IDでユーザー一覧取得
     * GET /api/users/department/{departmentId}
     */
    @GetMapping("/department/{departmentId}")
    public ResponseEntity<List<UserDto>> getUsersByDepartmentId(@PathVariable Long departmentId) {
        log.debug("部門別ユーザー一覧取得API呼び出し: departmentId={}", departmentId);
        List<UserDto> users = userService.findByDepartmentId(departmentId);
        return ResponseEntity.ok(users);
    }

    /**
     * 組織IDでユーザー一覧取得
     * GET /api/users/organization/{organizationId}
     */
    @GetMapping("/organization/{organizationId}")
    public ResponseEntity<List<UserDto>> getUsersByOrganizationId(@PathVariable Long organizationId) {
        log.debug("組織別ユーザー一覧取得API呼び出し: organizationId={}", organizationId);
        List<UserDto> users = userService.findByOrganizationId(organizationId);
        return ResponseEntity.ok(users);
    }

    /**
     * ユーザー作成
     * POST /api/users
     */
    @PostMapping
    public ResponseEntity<UserDto> createUser(@Valid @RequestBody UserDto userDto) {
        log.debug("ユーザー作成API呼び出し: {}", userDto.getName());
        UserDto created = userService.create(userDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    /**
     * ユーザー更新
     * PUT /api/users/{id}
     */
    @PutMapping("/{id}")
    public ResponseEntity<UserDto> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UserDto userDto) {
        log.debug("ユーザー更新API呼び出し: ID={}", id);
        UserDto updated = userService.update(id, userDto);
        return ResponseEntity.ok(updated);
    }

    /**
     * ユーザー削除
     * DELETE /api/users/{id}
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        log.debug("ユーザー削除API呼び出し: ID={}", id);
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
