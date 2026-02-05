package com.example.orgmgmt.service;

import com.example.orgmgmt.dto.UserDTO;
import com.example.orgmgmt.entity.Department;
import com.example.orgmgmt.entity.User;
import com.example.orgmgmt.exception.DuplicateResourceException;
import com.example.orgmgmt.exception.ResourceNotFoundException;
import com.example.orgmgmt.repository.DepartmentRepository;
import com.example.orgmgmt.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class UserService {

    private final UserRepository userRepository;
    private final DepartmentRepository departmentRepository;
    private final EntityMapper entityMapper;

    public UserDTO createUser(User user) {
        if (userRepository.existsByUsername(user.getUsername())) {
            throw new DuplicateResourceException("User with username " + user.getUsername() + " already exists");
        }

        if (userRepository.existsByEmail(user.getEmail())) {
            throw new DuplicateResourceException("User with email " + user.getEmail() + " already exists");
        }

        if (userRepository.existsByEmployeeNumber(user.getEmployeeNumber())) {
            throw new DuplicateResourceException("User with employee number " + user.getEmployeeNumber() + " already exists");
        }

        if (user.getDepartment() != null && user.getDepartment().getId() != null) {
            Department department = departmentRepository.findById(user.getDepartment().getId())
                .orElseThrow(() -> new ResourceNotFoundException("Department not found with id: " + user.getDepartment().getId()));
            user.setDepartment(department);
        }

        User saved = userRepository.save(user);
        return entityMapper.toDTO(saved);
    }

    @Transactional(readOnly = true)
    public UserDTO getUserById(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + id));
        return entityMapper.toDTO(user);
    }

    @Transactional(readOnly = true)
    public UserDTO getUserByUsername(String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with username: " + username));
        return entityMapper.toDTO(user);
    }

    @Transactional(readOnly = true)
    public UserDTO getUserByEmail(String email) {
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with email: " + email));
        return entityMapper.toDTO(user);
    }

    @Transactional(readOnly = true)
    public UserDTO getUserByEmployeeNumber(String employeeNumber) {
        User user = userRepository.findByEmployeeNumber(employeeNumber)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with employee number: " + employeeNumber));
        return entityMapper.toDTO(user);
    }

    @Transactional(readOnly = true)
    public List<UserDTO> getAllUsers() {
        return userRepository.findAll().stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<UserDTO> getAllUsers(Pageable pageable) {
        return userRepository.findAll(pageable)
            .map(entityMapper::toDTO);
    }

    @Transactional(readOnly = true)
    public List<UserDTO> getUsersByDepartment(Long departmentId) {
        return userRepository.findByDepartmentId(departmentId).stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<UserDTO> getActiveUsers() {
        return userRepository.findByActiveTrue().stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<UserDTO> searchUsers(String search, Pageable pageable) {
        return userRepository.searchUsers(search, pageable)
            .map(entityMapper::toDTO);
    }

    public UserDTO updateUser(Long id, User userDetails) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + id));

        if (!user.getUsername().equals(userDetails.getUsername()) &&
            userRepository.existsByUsername(userDetails.getUsername())) {
            throw new DuplicateResourceException("User with username " + userDetails.getUsername() + " already exists");
        }

        if (!user.getEmail().equals(userDetails.getEmail()) &&
            userRepository.existsByEmail(userDetails.getEmail())) {
            throw new DuplicateResourceException("User with email " + userDetails.getEmail() + " already exists");
        }

        if (!user.getEmployeeNumber().equals(userDetails.getEmployeeNumber()) &&
            userRepository.existsByEmployeeNumber(userDetails.getEmployeeNumber())) {
            throw new DuplicateResourceException("User with employee number " + userDetails.getEmployeeNumber() + " already exists");
        }

        user.setUsername(userDetails.getUsername());
        user.setEmail(userDetails.getEmail());
        user.setEmployeeNumber(userDetails.getEmployeeNumber());
        user.setFirstName(userDetails.getFirstName());
        user.setLastName(userDetails.getLastName());
        user.setActive(userDetails.getActive());

        if (userDetails.getDepartment() != null && userDetails.getDepartment().getId() != null) {
            Department department = departmentRepository.findById(userDetails.getDepartment().getId())
                .orElseThrow(() -> new ResourceNotFoundException("Department not found"));
            user.setDepartment(department);
        }

        User updated = userRepository.save(user);
        return entityMapper.toDTO(updated);
    }

    public void deleteUser(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + id));
        userRepository.delete(user);
    }

    public UserDTO deactivateUser(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + id));
        user.setActive(false);
        User updated = userRepository.save(user);
        return entityMapper.toDTO(updated);
    }
}
