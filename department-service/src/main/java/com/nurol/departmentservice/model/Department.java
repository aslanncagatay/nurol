package com.nurol.departmentservice.model;

import java.util.ArrayList;
import java.util.List;

public class Department {
    private Long id;
    private String name;
    private String phone;
    private String location;
    private Long budget;
    private List<Employee> employees = new ArrayList<>();

    public Department() {
    }

    public Department(Long id, String name, String phone, String location, Long budget, List<Employee> employees) {
        this.id = id;
        this.name = name;
        this.phone = phone;
        this.location = location;
        this.budget = budget;
    }

    @Override
    public String toString() {
        return "Department{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", phone='" + phone + '\'' +
                ", location='" + location + '\'' +
                ", budget=" + budget +
                '}';
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public Long getBudget() {
        return budget;
    }

    public void setBudget(Long budget) {
        this.budget = budget;
    }


    public List<Employee> getEmployees() {
        return employees;
    }

    public void setEmployees(List<Employee> employees) {
        this.employees = employees;
    }
}
