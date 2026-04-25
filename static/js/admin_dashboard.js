
        // function fetch_users_stats() {
        //     fetch('/admin/users')
        //         .then(res => res.json())
        //         .then(users => {
                    
        //         })
        // }



        async function fetch_users_stats() {
            try {
                const res = await fetch('/admin/users');
                const data = await res.json();
                console.log(data);
                populateUsersTable(data.users); // ✅ real DB users
                document.querySelector('.number').textContent = data.total_users;
            } catch (error) {
                console.error('Error fetching users:', error);
            }
        }

            async function fetch_users_stats() {
            try {
                const res = await fetch('/admin/users');
                const data = await res.json();
                console.log(data);
                populateUsersTable(data.users); // ✅ real DB users
                document.querySelector('.number').textContent = data.total_users;
            } catch (error) {
                console.error('Error fetching users:', error);
            }
        }



        // DOM Elements
        const mobileToggle = document.getElementById('mobileToggle');
        const sidebar = document.getElementById('sidebar');
        const usersTableBody = document.getElementById('usersTableBody');
        const notifications = document.querySelector('.notifications');
        const notificationCount = document.querySelector('.notification-count');

        // Toggle sidebar on mobile
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (event) => {
            if (window.innerWidth <= 992 && !sidebar.contains(event.target) && !mobileToggle.contains(event.target)) {
                sidebar.classList.remove('active');
            }
        });

        // Populate users table
        function populateUsersTable(users) {
            usersTableBody.innerHTML = '';
            
            users.forEach(user => {
                const row = document.createElement('tr');
                
                // Get initials for avatar
                const nameParts = user.name.split(' ');
                const initials = nameParts[0].charAt(0) + (nameParts[1] ? nameParts[1].charAt(0) : '');
                
                // Status class
                let statusClass = '';
                if (user.status === 'active') statusClass = 'active';
                else if (user.status === 'pending') statusClass = 'pending';
                else statusClass = 'inactive';
                
                row.innerHTML = `
                    <td>
                        <div class="user-cell">
                            <div class="user-avatar-small">${initials}</div>
                            <div>${user.name}</div>
                        </div>
                    </td>
                    <td>${user.email}</td>
                    <td>${new Date(user.joinDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</td>
                    <td><span class="status ${statusClass}">${user.status.charAt(0).toUpperCase() + user.status.slice(1)}</span></td>
                    <td>
                        <button class="btn-view" data-id="${user.id}">View</button>
                    </td>
                `;
                
                usersTableBody.appendChild(row);
            });
            
            // Add event listeners to view buttons
            document.querySelectorAll('.btn-view').forEach(button => {
                button.addEventListener('click', function() {
                    const userId = this.getAttribute('data-id');
                    alert(`Viewing user with ID: ${userId}`);
                });
            });
        }

        // Toggle notifications
        notifications.addEventListener('click', () => {
            alert('You have 3 new notifications:\n- New user registered\n- Payment received\n- System updated');
            notificationCount.textContent = '0';
            notificationCount.style.backgroundColor = 'var(--gray)';
        });

        // Chart.js for revenue chart
        function initChart() {
            const ctx = document.getElementById('revenueChart').getContext('2d');
            
            // Create gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(67, 97, 238, 0.5)');
            gradient.addColorStop(1, 'rgba(67, 97, 238, 0.1)');
            
            // Chart data
            const data = {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Revenue',
                    data: [12000, 15000, 18000, 14000, 22000, 24580, 20000, 23000, 21000, 25000, 28000, 30000],
                    backgroundColor: gradient,
                    borderColor: 'var(--primary)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            };
            
            // Chart configuration
            const config = {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return `Revenue: $${context.parsed.y.toLocaleString()}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            };
            
            // Create chart
            new Chart(ctx, config);
        }

        // Initialize the dashboard
        document.addEventListener('DOMContentLoaded', () => {
            console.log('Admin dashboard loaded')
            // populateUsersTable();
                fetch_users_stats();

            initChart();
            
            // Set active navigation
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    document.querySelectorAll('.nav-links a').forEach(item => {
                        item.classList.remove('active');
                    });
                    this.classList.add('active');
                    
                    // Close sidebar on mobile after clicking a link
                    if (window.innerWidth <= 992) {
                        sidebar.classList.remove('active');
                    }
                });
            });
        });