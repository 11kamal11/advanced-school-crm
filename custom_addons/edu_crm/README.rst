==========
School CRM
==========

.. |badge1| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1|

**Enterprise-grade school management suite** built on Odoo, unifying the
admissions CRM pipeline, day-to-day academic operations, finance, assets,
a public marketing website and a parent/student self-service portal in a
single application.

Overview
========

School CRM extends Odoo with a full education-vertical data model and
workflow, from a prospective family's first inquiry through enrollment,
academics, attendance, examinations, fee collection and asset management —
backed by a public website for admissions marketing and a portal for
guardians/students.

Key Functionality
==================

Admissions CRM
--------------
* Admission inquiries (leads) with a configurable pipeline of stages
  (``edu.crm.stage``) and lost-reason tracking, built on Odoo's CRM/UTM
  infrastructure for source and campaign attribution.
* Application intake (``edu.applicant``) with a guided enrollment wizard to
  convert an accepted applicant directly into a student record.
* A lead-to-application conversion wizard to move qualified inquiries
  forward without re-entering data.

Academics
---------
* Academic Year, Program, Class/Section and Subject master data.
* Timetable slots per class/subject/teacher.
* Exam scheduling and result recording (``edu.exam`` / ``edu.exam.result``).
* Attendance sessions with per-student attendance lines and a bulk
  attendance-entry wizard.

Student & Guardian Management
------------------------------
* Central Student record linked to one or more Guardians/Parents, class,
  program and academic year.
* Guardian portal access so parents can follow their child's academics,
  attendance and fees online.

Staff Management
-----------------
* Teacher records and leave-request workflow with approval tracking.

Finance
-------
* Configurable Fee Structures, per-student Fee assessment and a fee-payment
  wizard integrated with Odoo's ``payment`` module for online/offline
  collection and reconciliation.

Assets
------
* School Asset and Asset Category registry with a checkout/return wizard to
  track equipment issued to staff, students or classes.

Reporting & Dashboard
-----------------------
* A consolidated School CRM dashboard and analysis views/reports for
  admissions, academics and finance.

Website & Portal
------------------
* Public website pages covering admissions, features, and each core module
  (students, attendance, academics, teachers, exams/results, fees), backed
  by Odoo's ``website`` app for full page-builder editing.
* A parent/student portal (``portal`` app) exposing applications, fees,
  attendance and results to authenticated guardians/students.
* Automated notifications via configurable mail templates and scheduled
  actions (``data/edu_mail_templates.xml``, ``data/edu_cron_data.xml``).

Automation & Data
-------------------
* Sequence-based numbering for key records.
* A demo-data wizard to populate a working environment for evaluation or
  training.

Who It's For
============

Designed to scale from a single small school through a multi-branch
institution: every academic entity (year, program, class, subject) is
freely configurable rather than hard-coded, so the same module fits a
primary school, a secondary school, or a K-12 institution running both.

Technical Information
======================

* **Depends on:** ``base``, ``mail``, ``portal``, ``website``, ``utm``,
  ``payment``
* **License:** LGPL-3
* **Odoo Series:** 19.0

Bug Tracker
============

Bugs are tracked on the module's repository issue tracker. In case of
trouble, please report the issue there, including steps to reproduce.

Credits
========

Authors
-------

* Kamal Pant
