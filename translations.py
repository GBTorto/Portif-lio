"""
Translation system for the portfolio
"""

translations = {
    'en': {
        # Navigation
        'home': 'Home',
        'about': 'About',
        'portfolio': 'Portfolio',
        'login': 'Login',
        'logout': 'Logout',
        'admin': 'Admin',
        'profile': 'Profile',
        'edit_profile': 'Edit Profile',
        
        # Home page
        'welcome': 'Welcome to Gabriel Morais Portfolio',
        'featured_projects': 'Featured Projects',
        'recent_projects': 'Recent Projects',
        'view_project': 'View Project',
        'sort_by_recent': 'Sort by Recent',
        'sort_by_popular': 'Sort by Popular',
        
        # About page
        'about_me': 'About Me',
        'achievements': 'Achievements',
        'experience': 'Experience',
        'skills': 'Skills',
        'download_resume': 'Download Resume',
        
        # Portfolio page
        'all_projects': 'All Projects',
        'search_projects': 'Search projects...',
        'filter_by_category': 'Filter by Category',
        'filter_by_tag': 'Filter by Tag',
        'no_projects_found': 'No projects found',
        
        # Profile page
        'user_profile': 'User Profile',
        'comments_posted': 'Comments Posted',
        'projects_liked': 'Projects Liked',
        'years_active': 'Years Active',
        'recent_comments': 'Recent Comments',
        'liked_projects': 'Liked Projects',
        'social_networks': 'Social Networks',
        'add_social_network': 'Add Social Network',
        'remove_social_network': 'Remove Social Network',
        
        # Forms
        'username': 'Username',
        'email': 'Email',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'description': 'Description',
        'save_changes': 'Save Changes',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'confirm': 'Confirm',
        
        # Social Networks
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'twitter': 'Twitter',
        'instagram': 'Instagram',
        'website': 'Website',
        'add_network': 'Add Network',
        'network_name': 'Network Name',
        'network_url': 'Network URL',
        
        # Confirmation Dialog
        'confirm_delete': 'Confirm Deletion',
        'delete_social_network_message': 'Are you sure you want to remove this social network?',
        'dont_ask_again': "Don't ask again",
        
        # Messages
        'profile_updated': 'Profile updated successfully!',
        'social_network_added': 'Social network added successfully!',
        'social_network_removed': 'Social network removed successfully!',
        'invalid_url': 'Please enter a valid URL',
        'required_field': 'This field is required',
        
        # Admin
        'admin_panel': 'Admin Panel',
        'manage_projects': 'Manage Projects',
        'manage_users': 'Manage Users',
        'site_settings': 'Site Settings',
        
        # Footer
        'all_rights_reserved': 'All rights reserved',
        'built_with': 'Built with Flask'
    },
    'pt': {
        # Navigation
        'home': 'Início',
        'about': 'Sobre',
        'portfolio': 'Portfólio',
        'login': 'Entrar',
        'logout': 'Sair',
        'admin': 'Admin',
        'profile': 'Perfil',
        'edit_profile': 'Editar Perfil',
        
        # Home page
        'welcome': 'Bem-vindo ao Portfólio de Gabriel Morais',
        'featured_projects': 'Projetos em Destaque',
        'recent_projects': 'Projetos Recentes',
        'view_project': 'Ver Projeto',
        'sort_by_recent': 'Ordenar por Recentes',
        'sort_by_popular': 'Ordenar por Populares',
        
        # About page
        'about_me': 'Sobre Mim',
        'achievements': 'Conquistas',
        'experience': 'Experiência',
        'skills': 'Habilidades',
        'download_resume': 'Baixar Currículo',
        
        # Portfolio page
        'all_projects': 'Todos os Projetos',
        'search_projects': 'Pesquisar projetos...',
        'filter_by_category': 'Filtrar por Categoria',
        'filter_by_tag': 'Filtrar por Tag',
        'no_projects_found': 'Nenhum projeto encontrado',
        
        # Profile page
        'user_profile': 'Perfil do Usuário',
        'comments_posted': 'Comentários Postados',
        'projects_liked': 'Projetos Curtidos',
        'years_active': 'Anos Ativo',
        'recent_comments': 'Comentários Recentes',
        'liked_projects': 'Projetos Curtidos',
        'social_networks': 'Redes Sociais',
        'add_social_network': 'Adicionar Rede Social',
        'remove_social_network': 'Remover Rede Social',
        
        # Forms
        'username': 'Nome de Usuário',
        'email': 'E-mail',
        'password': 'Senha',
        'confirm_password': 'Confirmar Senha',
        'description': 'Descrição',
        'save_changes': 'Salvar Alterações',
        'cancel': 'Cancelar',
        'delete': 'Excluir',
        'confirm': 'Confirmar',
        
        # Social Networks
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'twitter': 'Twitter',
        'instagram': 'Instagram',
        'website': 'Site',
        'add_network': 'Adicionar Rede',
        'network_name': 'Nome da Rede',
        'network_url': 'URL da Rede',
        
        # Confirmation Dialog
        'confirm_delete': 'Confirmar Exclusão',
        'delete_social_network_message': 'Tem certeza de que deseja remover esta rede social?',
        'dont_ask_again': 'Não perguntar novamente',
        
        # Messages
        'profile_updated': 'Perfil atualizado com sucesso!',
        'social_network_added': 'Rede social adicionada com sucesso!',
        'social_network_removed': 'Rede social removida com sucesso!',
        'invalid_url': 'Por favor, insira uma URL válida',
        'required_field': 'Este campo é obrigatório',
        
        # Admin
        'admin_panel': 'Painel Admin',
        'manage_projects': 'Gerenciar Projetos',
        'manage_users': 'Gerenciar Usuários',
        'site_settings': 'Configurações do Site',
        
        # Footer
        'all_rights_reserved': 'Todos os direitos reservados',
        'built_with': 'Desenvolvido com Flask'
    }
}

def get_text(key, lang='en'):
    """Get translated text for a key and language"""
    return translations.get(lang, translations['en']).get(key, key)

def get_available_languages():
    """Get list of available language codes"""
    return list(translations.keys())