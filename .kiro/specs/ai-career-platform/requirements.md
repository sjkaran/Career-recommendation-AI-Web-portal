# Requirements Document

## Introduction

An AI-driven career recommendation and internship matching platform designed for BPUT (Biju Patnaik University of Technology) students, employers, and placement officers. The platform creates automated digital profiles for students, provides career recommendations using predictive models, enables job/internship posting and matching, and offers analytics dashboards for institutional decision-making. This is a lightweight demo version utilizing free AI APIs with a simple blue and grey theme.

## Glossary

- **Career_Platform**: The main AI-driven career recommendation and internship matching system
- **Student_Profile**: Automated digital profile containing skills, academic, co-curricular and extra-curricular data
- **Recommendation_Engine**: AI-based system that maps student attributes to suitable career domains
- **Matching_Algorithm**: AI algorithm that shortlists candidates for job/internship postings
- **Analytics_Dashboard**: Visual interface showing placement trends, skill gaps, and industry forecasts
- **Placement_Officer**: College staff member managing student placements and career guidance
- **Employer_Portal**: Interface for employers to post jobs, manage applications, and track candidates
- **BPUT**: Biju Patnaik University of Technology - the target educational institution

## Requirements

### Requirement 1

**User Story:** As a student, I want to create an automated digital profile by inputting my skills, academic records, and activities, so that I can receive personalized career recommendations and job matches.

#### Acceptance Criteria

1. WHEN a student registers on the Career_Platform, THE Career_Platform SHALL create a Student_Profile with personal information fields
2. THE Career_Platform SHALL provide input forms for academic records, technical skills, co-curricular activities, and extra-curricular achievements
3. WHEN a student completes their profile information, THE Career_Platform SHALL validate and store the data in the Student_Profile
4. THE Career_Platform SHALL support profile updates and modifications at any time
5. WHERE English or Odia language is selected, THE Career_Platform SHALL display the interface in the chosen language

### Requirement 2

**User Story:** As a student, I want to receive AI-powered career recommendations based on my profile, so that I can make informed decisions about my career path.

#### Acceptance Criteria

1. WHEN a Student_Profile is complete, THE Recommendation_Engine SHALL analyze student attributes using AI algorithms
2. THE Recommendation_Engine SHALL generate career domain recommendations with confidence scores
3. THE Career_Platform SHALL display recommended career paths with explanations and required skills
4. WHEN new data is added to a Student_Profile, THE Recommendation_Engine SHALL update recommendations accordingly
5. THE Career_Platform SHALL provide career roadmaps and skill development suggestions for each recommendation

### Requirement 3

**User Story:** As an employer, I want to post job and internship opportunities with specific requirements, so that I can find suitable candidates through AI-powered matching.

#### Acceptance Criteria

1. WHEN an employer accesses the Employer_Portal, THE Career_Platform SHALL provide job posting forms with requirement fields
2. THE Career_Platform SHALL allow employers to specify skills, qualifications, experience levels, and other criteria
3. WHEN a job is posted, THE Matching_Algorithm SHALL automatically shortlist relevant candidates from Student_Profiles
4. THE Employer_Portal SHALL display candidate matches with compatibility scores and profile summaries
5. THE Career_Platform SHALL enable employers to provide feedback on candidate recommendations for algorithm improvement

### Requirement 4

**User Story:** As a placement officer, I want to access analytics dashboards showing placement trends and skill gaps, so that I can make data-driven decisions for curriculum and policy improvements.

#### Acceptance Criteria

1. WHEN a placement officer logs into the Analytics_Dashboard, THE Career_Platform SHALL display visual insights on skill gap analysis by department
2. THE Analytics_Dashboard SHALL show placement trends filtered by branch and district
3. THE Career_Platform SHALL generate industry-wise demand forecasts using historical and current data
4. THE Analytics_Dashboard SHALL provide exportable reports in PDF and Excel formats
5. THE Career_Platform SHALL update analytics data in real-time as new placements and profiles are added

### Requirement 5

**User Story:** As a system administrator, I want to ensure secure access and data privacy across all user roles, so that sensitive student and employer information is protected.

#### Acceptance Criteria

1. THE Career_Platform SHALL implement role-based authentication for students, employers, and placement officers
2. WHEN users access the system, THE Career_Platform SHALL require secure login credentials and session management
3. THE Career_Platform SHALL encrypt all personal data and maintain GDPR-compliant privacy protocols
4. THE Career_Platform SHALL provide audit logs for all data access and modifications
5. THE Career_Platform SHALL implement data backup and recovery mechanisms

### Requirement 6

**User Story:** As a user, I want to access the platform seamlessly across mobile and web interfaces, so that I can use the system conveniently from any device.

#### Acceptance Criteria

1. THE Career_Platform SHALL provide responsive web design that adapts to mobile, tablet, and desktop screens
2. WHEN accessed on mobile devices, THE Career_Platform SHALL maintain full functionality with optimized user interface
3. THE Career_Platform SHALL ensure consistent user experience across different browsers and devices
4. THE Career_Platform SHALL implement touch-friendly navigation and input controls for mobile users
5. THE Career_Platform SHALL optimize loading times and minimize data usage for mobile connections

### Requirement 7

**User Story:** As a platform owner, I want to implement a sustainable financial model with freemium and institutional access options, so that the platform can maintain long-term operations and growth.

#### Acceptance Criteria

1. THE Career_Platform SHALL provide basic features free for students and limited employer access
2. THE Career_Platform SHALL offer premium subscriptions for employers with advanced matching and analytics features
3. THE Career_Platform SHALL provide institutional licensing for colleges with comprehensive administrative tools
4. THE Career_Platform SHALL implement usage tracking and billing systems for paid features
5. THE Career_Platform SHALL offer employer branding opportunities through sponsored content and featured listings