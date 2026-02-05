package com.example.orgmgmt.repository;

import com.example.orgmgmt.entity.Organization;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase.Replace.NONE;

@DataJpaTest
@AutoConfigureTestDatabase(replace = NONE)
class OrganizationRepositoryTest {

    @Autowired
    private OrganizationRepository organizationRepository;

    private Organization testOrganization;

    @BeforeEach
    void setUp() {
        organizationRepository.deleteAll();

        testOrganization = new Organization();
        testOrganization.setCode("TEST001");
        testOrganization.setName("Test Organization");
        testOrganization.setDescription("Test description");
        testOrganization.setEstablishedDate(LocalDate.of(2020, 1, 1));
        testOrganization.setActive(true);
    }

    @Test
    void testFindByCode_Success() {
        // Given
        organizationRepository.save(testOrganization);

        // When
        Optional<Organization> result = organizationRepository.findByCode("TEST001");

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getCode()).isEqualTo("TEST001");
        assertThat(result.get().getName()).isEqualTo("Test Organization");
    }

    @Test
    void testFindByCode_NotFound() {
        // When
        Optional<Organization> result = organizationRepository.findByCode("NOTEXIST");

        // Then
        assertThat(result).isEmpty();
    }

    @Test
    void testExistsByCode_True() {
        // Given
        organizationRepository.save(testOrganization);

        // When
        boolean exists = organizationRepository.existsByCode("TEST001");

        // Then
        assertThat(exists).isTrue();
    }

    @Test
    void testExistsByCode_False() {
        // When
        boolean exists = organizationRepository.existsByCode("NOTEXIST");

        // Then
        assertThat(exists).isFalse();
    }

    @Test
    void testFindByActiveTrue() {
        // Given
        Organization activeOrg = new Organization();
        activeOrg.setCode("ACTIVE001");
        activeOrg.setName("Active Org");
        activeOrg.setActive(true);
        organizationRepository.save(activeOrg);

        Organization inactiveOrg = new Organization();
        inactiveOrg.setCode("INACTIVE001");
        inactiveOrg.setName("Inactive Org");
        inactiveOrg.setActive(false);
        organizationRepository.save(inactiveOrg);

        // When
        List<Organization> activeOrgs = organizationRepository.findByActiveTrue();

        // Then
        assertThat(activeOrgs).hasSize(1);
        assertThat(activeOrgs.get(0).getCode()).isEqualTo("ACTIVE001");
    }

    @Test
    void testSearchOrganizations_ByName() {
        // Given
        organizationRepository.save(testOrganization);

        Organization anotherOrg = new Organization();
        anotherOrg.setCode("TEST002");
        anotherOrg.setName("Another Organization");
        anotherOrg.setActive(true);
        organizationRepository.save(anotherOrg);

        // When
        Page<Organization> results = organizationRepository.searchOrganizations(
            "Test", null, null, null, PageRequest.of(0, 10));

        // Then
        assertThat(results.getContent()).hasSize(1);
        assertThat(results.getContent().get(0).getName()).contains("Test");
    }

    @Test
    void testSearchOrganizations_ByCode() {
        // Given
        organizationRepository.save(testOrganization);

        // When
        Page<Organization> results = organizationRepository.searchOrganizations(
            null, "TEST001", null, null, PageRequest.of(0, 10));

        // Then
        assertThat(results.getContent()).hasSize(1);
        assertThat(results.getContent().get(0).getCode()).isEqualTo("TEST001");
    }

    @Test
    void testSearchOrganizations_ByActive() {
        // Given
        organizationRepository.save(testOrganization);

        Organization inactiveOrg = new Organization();
        inactiveOrg.setCode("INACTIVE001");
        inactiveOrg.setName("Inactive Org");
        inactiveOrg.setActive(false);
        organizationRepository.save(inactiveOrg);

        // When
        Page<Organization> results = organizationRepository.searchOrganizations(
            null, null, true, null, PageRequest.of(0, 10));

        // Then
        assertThat(results.getContent()).hasSize(1);
        assertThat(results.getContent().get(0).isActive()).isTrue();
    }

    @Test
    void testSearchOrganizations_NoFilters() {
        // Given
        organizationRepository.save(testOrganization);

        Organization anotherOrg = new Organization();
        anotherOrg.setCode("TEST002");
        anotherOrg.setName("Another Organization");
        anotherOrg.setActive(true);
        organizationRepository.save(anotherOrg);

        // When
        Page<Organization> results = organizationRepository.searchOrganizations(
            null, null, null, null, PageRequest.of(0, 10));

        // Then
        assertThat(results.getContent()).hasSize(2);
    }
}
