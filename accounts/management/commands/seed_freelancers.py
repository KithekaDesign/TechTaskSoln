"""
Management command to seed 8 professional freelancer profiles.
Usage: python manage.py seed_freelancers
"""
from django.core.management.base import BaseCommand
from accounts.models import User, FreelancerProfile


FREELANCERS = [
    {
        'username': 'sarah_chen',
        'email': 'sarah.chen@techmail.com',
        'first_name': 'Sarah',
        'last_name': 'Chen',
        'bio': 'Senior full-stack developer with 8+ years building scalable web platforms. Specializing in React, Node.js, and cloud-native architectures. Former lead engineer at a Series B startup. Passionate about clean code and developer experience.',
        'profile': {
            'skills': 'React, Node.js, TypeScript, PostgreSQL, AWS, Docker, GraphQL, Next.js',
            'experience_level': 'Expert',
            'category': 'web_development',
            'hourly_rate': 85.00,
            'rating': 4.9,
            'completed_projects': 47,
            'portfolio_link': 'https://sarahchen.dev',
            'title': 'Senior Full-Stack Engineer',
            'location': 'San Francisco, USA',
            'languages': 'English, Mandarin',
            'availability': 'available',
            'eth_wallet_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f2bD38',
            'total_earnings': 12.5,
        },
    },
    {
        'username': 'james_ochieng',
        'email': 'james.ochieng@devmail.com',
        'first_name': 'James',
        'last_name': 'Ochieng',
        'bio': 'Data Scientist and Machine Learning Engineer with expertise in predictive modeling, NLP, and computer vision. Published researcher with experience deploying ML models at scale using TensorFlow and PyTorch.',
        'profile': {
            'skills': 'Python, TensorFlow, PyTorch, Pandas, Scikit-learn, SQL, Apache Spark, Jupyter',
            'experience_level': 'Expert',
            'category': 'data_science',
            'hourly_rate': 95.00,
            'rating': 4.8,
            'completed_projects': 32,
            'portfolio_link': 'https://jamesochieng.io',
            'title': 'Lead Data Scientist',
            'location': 'Nairobi, Kenya',
            'languages': 'English, Swahili',
            'availability': 'available',
            'eth_wallet_address': '0x8ba1f109551bD432803012645Ac136ddd64DBA72',
            'total_earnings': 8.2,
        },
    },
    {
        'username': 'priya_sharma',
        'email': 'priya.sharma@aiworks.com',
        'first_name': 'Priya',
        'last_name': 'Sharma',
        'bio': 'AI/ML specialist focused on building production-grade LLM applications, recommendation systems, and intelligent automation pipelines. Google-certified ML engineer with Fortune 500 consulting experience.',
        'profile': {
            'skills': 'Python, LangChain, OpenAI API, Hugging Face, MLOps, Kubernetes, FastAPI, Redis',
            'experience_level': 'Expert',
            'category': 'ai_ml',
            'hourly_rate': 110.00,
            'rating': 5.0,
            'completed_projects': 28,
            'portfolio_link': 'https://priyasharma.ai',
            'title': 'AI/ML Solutions Architect',
            'location': 'Bangalore, India',
            'languages': 'English, Hindi',
            'availability': 'busy',
            'eth_wallet_address': '0xdD2FD4581271e230360230F9337D5c0430Bf44C0',
            'total_earnings': 15.8,
        },
    },
    {
        'username': 'michael_wright',
        'email': 'michael.wright@cloudops.dev',
        'first_name': 'Michael',
        'last_name': 'Wright',
        'bio': 'AWS Solutions Architect and DevOps engineer specializing in cloud migrations, infrastructure as code, and CI/CD pipeline optimization. Certified in AWS, Azure, and GCP with 10+ years of experience.',
        'profile': {
            'skills': 'AWS, Terraform, Kubernetes, Docker, Jenkins, GitHub Actions, Ansible, Linux',
            'experience_level': 'Expert',
            'category': 'cloud_infra',
            'hourly_rate': 100.00,
            'rating': 4.7,
            'completed_projects': 55,
            'portfolio_link': 'https://mwright-cloud.com',
            'title': 'Senior Cloud & DevOps Engineer',
            'location': 'London, UK',
            'languages': 'English',
            'availability': 'available',
            'eth_wallet_address': '0xFABB0ac9d68B0B445fB7357272Ff202C5651694a',
            'total_earnings': 22.1,
        },
    },
    {
        'username': 'amara_konteh',
        'email': 'amara.konteh@appcraft.io',
        'first_name': 'Amara',
        'last_name': 'Konteh',
        'bio': 'Mobile app developer crafting native iOS and Android experiences with Swift and Kotlin. Also proficient in Flutter for cross-platform builds. Strong focus on UX, performance, and App Store optimization.',
        'profile': {
            'skills': 'Swift, Kotlin, Flutter, Dart, Firebase, Figma, React Native, Xcode',
            'experience_level': 'Intermediate',
            'category': 'app_development',
            'hourly_rate': 70.00,
            'rating': 4.6,
            'completed_projects': 19,
            'portfolio_link': 'https://amaraapps.dev',
            'title': 'Mobile App Developer',
            'location': 'Lagos, Nigeria',
            'languages': 'English, Yoruba, French',
            'availability': 'available',
            'eth_wallet_address': '0x71C7656EC7ab88b098defB751B7401B5f6d8976F',
            'total_earnings': 5.3,
        },
    },
    {
        'username': 'david_kimani',
        'email': 'david.kimani@netpro.co.ke',
        'first_name': 'David',
        'last_name': 'Kimani',
        'bio': 'Network architect and systems administrator with deep expertise in enterprise networking, Cisco infrastructure, SD-WAN, and network security. CCNP and CCNA certified with experience managing datacenter operations.',
        'profile': {
            'skills': 'Cisco, Juniper, SD-WAN, Firewall, MPLS, BGP, OSPF, Network Monitoring',
            'experience_level': 'Expert',
            'category': 'networking',
            'hourly_rate': 75.00,
            'rating': 4.5,
            'completed_projects': 23,
            'portfolio_link': 'https://dkimani-net.com',
            'title': 'Senior Network Architect',
            'location': 'Nairobi, Kenya',
            'languages': 'English, Swahili',
            'availability': 'available',
            'eth_wallet_address': '0x2546BcD3c84621e976D8185a91A922aE77ECEc30',
            'total_earnings': 6.7,
        },
    },
    {
        'username': 'elena_vasquez',
        'email': 'elena.vasquez@designstudio.com',
        'first_name': 'Elena',
        'last_name': 'Vasquez',
        'bio': 'Creative graphic designer and brand strategist with a portfolio spanning tech startups, SaaS brands, and e-commerce platforms. Expert in visual identity, UI illustrations, motion graphics, and print design.',
        'profile': {
            'skills': 'Figma, Adobe Photoshop, Illustrator, After Effects, Blender, UI Design, Branding',
            'experience_level': 'Intermediate',
            'category': 'graphic_design',
            'hourly_rate': 65.00,
            'rating': 4.8,
            'completed_projects': 41,
            'portfolio_link': 'https://elenavasquez.design',
            'title': 'Graphic Designer & Brand Strategist',
            'location': 'Mexico City, Mexico',
            'languages': 'English, Spanish',
            'availability': 'available',
            'eth_wallet_address': '0xbDA5747bFD65F08deb54cb465eB87D40e51B197E',
            'total_earnings': 9.4,
        },
    },
    {
        'username': 'alex_security',
        'email': 'alex.novak@cybershield.io',
        'first_name': 'Alex',
        'last_name': 'Novak',
        'bio': 'Certified Ethical Hacker (CEH) and cybersecurity consultant with extensive experience in penetration testing, vulnerability assessment, SOC operations, and security architecture. OSCP and CISSP certified.',
        'profile': {
            'skills': 'Penetration Testing, Burp Suite, Nmap, Metasploit, SIEM, Wireshark, Python, SOC',
            'experience_level': 'Expert',
            'category': 'cybersecurity',
            'hourly_rate': 120.00,
            'rating': 4.9,
            'completed_projects': 36,
            'portfolio_link': 'https://alexnovak-sec.com',
            'title': 'Senior Cybersecurity Consultant',
            'location': 'Berlin, Germany',
            'languages': 'English, German, Czech',
            'availability': 'busy',
            'eth_wallet_address': '0xcd3B766CCDd6AE721141F452C550Ca635964ce71',
            'total_earnings': 18.6,
        },
    },
]

DEFAULT_PASSWORD = 'Freelancer@2024'


class Command(BaseCommand):
    help = 'Seeds the database with 8 professional freelancer profiles'

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for fl in FREELANCERS:
            if User.objects.filter(username=fl['username']).exists():  # type: ignore[attr-defined]
                self.stdout.write(self.style.WARNING(  # type: ignore[attr-defined]
                    f"  Skipped {fl['username']} (already exists)"
                ))
                skipped_count += 1
                continue

            user = User.objects.create_user(
                username=fl['username'],
                email=fl['email'],
                password=DEFAULT_PASSWORD,
                first_name=fl['first_name'],
                last_name=fl['last_name'],
                bio=fl['bio'],
                is_freelancer=True,
                is_client=False,
                is_active=True,
                is_email_verified=True,
            )

            profile_data: dict = fl['profile']  # type: ignore[assignment]
            FreelancerProfile.objects.update_or_create(  # type: ignore[attr-defined]
                user=user,
                defaults=profile_data,
            )

            self.stdout.write(self.style.SUCCESS(  # type: ignore[attr-defined]
                f"  \u2713 Created {user.get_full_name()} ({user.email}) \u2014 {profile_data['category']}"
            ))
            created_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(  # type: ignore[attr-defined]
            f'Done! Created {created_count} freelancers, skipped {skipped_count}.'
        ))
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(  # type: ignore[attr-defined]
                f'Default login password: {DEFAULT_PASSWORD}'
            ))
