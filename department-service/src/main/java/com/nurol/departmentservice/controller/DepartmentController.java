package com.nurol.departmentservice.controller;

import com.nurol.departmentservice.client.EmployeeClient;
import com.nurol.departmentservice.model.Department;
import com.nurol.departmentservice.repository.DepartmentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/department")
public class DepartmentController {

    private static final Logger LOGGER
            = LoggerFactory.getLogger(DepartmentController.class);

    @Autowired
    private DepartmentRepository repository;

    @Autowired
    private EmployeeClient employeeClient;

    @PostMapping
    public Department add(@RequestBody Department department) {
        LOGGER.info("Department add: {}", department);
        return repository.addDepartment(department);
    }

    @GetMapping
    public List<Department> findAll() {
        LOGGER.info("Department find");
        return repository.findAll();
    }

    @GetMapping("/{id}")
    public Department findById(@PathVariable Long id) {
        LOGGER.info("Department find: id={}", id);
        return repository.findById(id);
    }

    @GetMapping("/with-employees/{id}")
    public Department findDepartmentWithEmployees(@PathVariable Long id) {
        LOGGER.info("Department find");
        Department department
                = repository.findById(id);
        department.setEmployees(
                employeeClient.findByDepartment(id));
        return  department;
    }

}
