package com.example;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {
    
    // Custom query method to find employees by first name
    List<Employee> findByFirstName(String firstName);
    
    // Custom query method to find employees by email
    Employee findByEmail(String email);
    
    // Custom query method to find employees by last name
    List<Employee> findByLastName(String lastName);
}