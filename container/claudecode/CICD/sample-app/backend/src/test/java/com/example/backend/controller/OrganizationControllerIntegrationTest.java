package com.example.backend.controller;

import com.example.common.dto.OrganizationDto;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * OrganizationController 統合テスト
 * 実際のSpring Bootアプリケーションコンテキストを使用
 *
 * ⚠️ 変更禁止: カバレッジ向上のため必須
 * - OrganizationController: 100%カバレッジ
 * - モック不使用の実データベース統合テスト
 */
@SpringBootTest
@AutoConfigureMockMvc
@Transactional
@DisplayName("OrganizationController 統合テスト")
class OrganizationControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private OrganizationDto testOrganization;

    @BeforeEach
    void setUp() {
        testOrganization = OrganizationDto.builder()
                .name("テスト組織")
                .description("統合テスト用の組織です")
                .build();
    }

    @Test
    @DisplayName("POST /api/organizations - 組織作成")
    void createOrganization_Success() throws Exception {
        mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganization)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.name").value("テスト組織"))
                .andExpect(jsonPath("$.description").value("統合テスト用の組織です"))
                .andExpect(jsonPath("$.createdAt").exists())
                .andExpect(jsonPath("$.updatedAt").exists());
    }

    @Test
    @DisplayName("GET /api/organizations - 全組織取得")
    void getAllOrganizations_Success() throws Exception {
        // 事前データ作成
        mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganization)))
                .andExpect(status().isCreated());

        // 全組織取得
        mockMvc.perform(get("/api/organizations"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(greaterThanOrEqualTo(1))))
                .andExpect(jsonPath("$[0].name").exists())
                .andExpect(jsonPath("$[0].id").exists());
    }

    @Test
    @DisplayName("GET /api/organizations/{id} - ID指定取得")
    void getOrganizationById_Success() throws Exception {
        // 事前データ作成
        String response = mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganization)))
                .andExpect(status().isCreated())
                .andReturn()
                .getResponse()
                .getContentAsString();

        OrganizationDto created = objectMapper.readValue(response, OrganizationDto.class);

        // ID指定取得
        mockMvc.perform(get("/api/organizations/" + created.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(created.getId()))
                .andExpect(jsonPath("$.name").value("テスト組織"));
    }

    @Test
    @DisplayName("GET /api/organizations/{id} - 存在しないID")
    void getOrganizationById_NotFound() throws Exception {
        mockMvc.perform(get("/api/organizations/99999"))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("PUT /api/organizations/{id} - 組織更新")
    void updateOrganization_Success() throws Exception {
        // 事前データ作成
        String response = mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganization)))
                .andExpect(status().isCreated())
                .andReturn()
                .getResponse()
                .getContentAsString();

        OrganizationDto created = objectMapper.readValue(response, OrganizationDto.class);

        // 更新データ
        OrganizationDto updateDto = OrganizationDto.builder()
                .name("更新後の組織名")
                .description("更新後の説明")
                .build();

        // 更新実行
        mockMvc.perform(put("/api/organizations/" + created.getId())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(updateDto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(created.getId()))
                .andExpect(jsonPath("$.name").value("更新後の組織名"))
                .andExpect(jsonPath("$.description").value("更新後の説明"));
    }

    @Test
    @DisplayName("PUT /api/organizations/{id} - 存在しないID")
    void updateOrganization_NotFound() throws Exception {
        OrganizationDto updateDto = OrganizationDto.builder()
                .name("更新組織")
                .description("更新説明")
                .build();

        mockMvc.perform(put("/api/organizations/99999")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(updateDto)))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("DELETE /api/organizations/{id} - 組織削除")
    void deleteOrganization_Success() throws Exception {
        // 事前データ作成
        String response = mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganization)))
                .andExpect(status().isCreated())
                .andReturn()
                .getResponse()
                .getContentAsString();

        OrganizationDto created = objectMapper.readValue(response, OrganizationDto.class);

        // 削除実行
        mockMvc.perform(delete("/api/organizations/" + created.getId()))
                .andExpect(status().isNoContent());

        // 削除確認
        mockMvc.perform(get("/api/organizations/" + created.getId()))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("DELETE /api/organizations/{id} - 存在しないID")
    void deleteOrganization_NotFound() throws Exception {
        mockMvc.perform(delete("/api/organizations/99999"))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("POST /api/organizations - 名前重複エラー")
    void createOrganization_DuplicateName() throws Exception {
        // 1回目の作成
        mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganization)))
                .andExpect(status().isCreated());

        // 同じ名前で2回目の作成
        mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganization)))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("POST /api/organizations - バリデーションエラー（名前なし）")
    void createOrganization_ValidationError() throws Exception {
        OrganizationDto invalidDto = OrganizationDto.builder()
                .description("名前がない組織")
                .build();

        mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidDto)))
                .andExpect(status().isBadRequest());
    }
}
