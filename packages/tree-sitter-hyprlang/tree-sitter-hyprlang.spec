Name:           tree-sitter-hyprlang
Version:        3.1.0
Release:        %autorelease
License:        MIT
URL:            https://github.com/tree-sitter-grammars/%{name}
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
BuildSystem:    tree_sitter

%{tree_sitter -l Hyprlang}

%changelog
%autochangelog
