package com.example;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.cfg.Configuration;

import java.util.List;

public class HibernateEmployeeDAO {
    private SessionFactory sessionFactory;
    
    public HibernateEmployeeDAO() {
        try {
            // Create SessionFactory from hibernate.cfg.xml
            sessionFactory = new Configuration().configure().buildSessionFactory();
        } catch (Throwable ex) {
            System.err.println("Initial SessionFactory creation failed." + ex);
            throw new ExceptionInInitializerError(ex);
        }
    }
    
    public Integer saveEmployee(Employee employee) {
        Session session = sessionFactory.getCurrentSession();
        Transaction transaction = null;
        Integer employeeId = null;
        
        try {
            transaction = session.beginTransaction();
            employeeId = (Integer) session.save(employee);
            transaction.commit();
        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
            e.printStackTrace();
        }
        
        return employeeId;
    }
    
    public List<Employee> listEmployees() {
        Session session = sessionFactory.getCurrentSession();
        Transaction transaction = null;
        List<Employee> employees = null;
        
        try {
            transaction = session.beginTransaction();
            employees = session.createQuery("FROM Employee", Employee.class).list();
            transaction.commit();
        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
            e.printStackTrace();
        }
        
        return employees;
    }
    
    public Employee getEmployee(Integer id) {
        Session session = sessionFactory.getCurrentSession();
        Transaction transaction = null;
        Employee employee = null;
        
        try {
            transaction = session.beginTransaction();
            employee = session.get(Employee.class, id);
            transaction.commit();
        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
            e.printStackTrace();
        }
        
        return employee;
    }
    
    public void updateEmployee(Employee employee) {
        Session session = sessionFactory.getCurrentSession();
        Transaction transaction = null;
        
        try {
            transaction = session.beginTransaction();
            session.update(employee);
            transaction.commit();
        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
            e.printStackTrace();
        }
    }
    
    public void deleteEmployee(Integer id) {
        Session session = sessionFactory.getCurrentSession();
        Transaction transaction = null;
        
        try {
            transaction = session.beginTransaction();
            Employee employee = session.get(Employee.class, id);
            if (employee != null) {
                session.delete(employee);
            }
            transaction.commit();
        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
            e.printStackTrace();
        }
    }
    
    public void shutdown() {
        sessionFactory.close();
    }
}