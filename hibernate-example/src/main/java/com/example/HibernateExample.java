package com.example;

import java.util.List;

public class HibernateExample {
    public static void main(String[] args) {
        HibernateEmployeeDAO employeeDAO = new HibernateEmployeeDAO();
        
        try {
            // Create employees
            Employee emp1 = new Employee("John", "Doe", "john.doe@email.com");
            Employee emp2 = new Employee("Jane", "Smith", "jane.smith@email.com");
            
            // Save employees
            Integer emp1Id = employeeDAO.saveEmployee(emp1);
            System.out.println("Employee created with ID: " + emp1Id);
            
            Integer emp2Id = employeeDAO.saveEmployee(emp2);
            System.out.println("Employee created with ID: " + emp2Id);
            
            // List all employees
            List<Employee> employees = employeeDAO.listEmployees();
            System.out.println("Retrieved " + employees.size() + " employees");
            for (Employee employee : employees) {
                System.out.println(employee);
            }
            
            // Get a specific employee
            Employee retrievedEmployee = employeeDAO.getEmployee(emp1Id);
            if (retrievedEmployee != null) {
                // Update employee
                retrievedEmployee.setEmail("john.doe.updated@email.com");
                employeeDAO.updateEmployee(retrievedEmployee);
                System.out.println("Employee updated successfully");
            }
            
            // Delete an employee
            employeeDAO.deleteEmployee(emp2Id);
            System.out.println("Employee deleted successfully");
            
        } finally {
            employeeDAO.shutdown();
        }
    }
}