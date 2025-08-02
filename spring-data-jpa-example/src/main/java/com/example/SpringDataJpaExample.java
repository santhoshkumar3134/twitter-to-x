package com.example;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;

@Component
public class SpringDataJpaExample implements CommandLineRunner {
    
    @Autowired
    private EmployeeService employeeService;
    
    @Override
    public void run(String... args) throws Exception {
        // Create employees
        Employee emp1 = new Employee("John", "Doe", "john.doe@email.com");
        Employee emp2 = new Employee("Jane", "Smith", "jane.smith@email.com");
        Employee emp3 = new Employee("John", "Wilson", "john.wilson@email.com");
        
        // Save employees
        emp1 = employeeService.saveEmployee(emp1);
        System.out.println("Employee created: " + emp1);
        
        emp2 = employeeService.saveEmployee(emp2);
        System.out.println("Employee created: " + emp2);
        
        emp3 = employeeService.saveEmployee(emp3);
        System.out.println("Employee created: " + emp3);
        
        // List all employees
        List<Employee> allEmployees = employeeService.getAllEmployees();
        System.out.println("Retrieved " + allEmployees.size() + " employees");
        
        // Find employees by first name
        List<Employee> johnEmployees = employeeService.getEmployeesByFirstName("John");
        System.out.println("Found " + johnEmployees.size() + " employees with first name: John");
        
        // Get a specific employee and update
        Optional<Employee> optionalEmployee = employeeService.getEmployeeById(emp1.getId());
        if (optionalEmployee.isPresent()) {
            Employee retrievedEmployee = optionalEmployee.get();
            retrievedEmployee.setEmail("john.doe.updated@email.com");
            Employee updatedEmployee = employeeService.updateEmployee(retrievedEmployee);
            System.out.println("Employee updated: " + updatedEmployee);
        }
        
        // Count employees
        long totalEmployees = employeeService.countEmployees();
        System.out.println("Total employees: " + totalEmployees);
        
        // Delete an employee
        employeeService.deleteEmployee(emp2.getId());
        System.out.println("Employee deleted with id: " + emp2.getId());
        
        // Count employees again
        totalEmployees = employeeService.countEmployees();
        System.out.println("Total employees: " + totalEmployees);
    }
}