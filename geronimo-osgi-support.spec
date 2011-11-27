%global registry geronimo-osgi-registry
%global locator geronimo-osgi-locator

Name:             geronimo-osgi-support
Version:          1.0
Release:          6
Summary:          OSGI spec bundle support
Group:            Development/Java
License:          ASL 2.0
URL:              http://geronimo.apache.org/

Source0:          http://repo2.maven.org/maven2/org/apache/geronimo/specs/%{name}/%{version}/%{name}-%{version}-source-release.tar.gz
Source1:          %{name}.depmap
# Use parent pom files instead of unavailable 'genesis-java5-flava'
Patch1:           use_parent_pom.patch
# Remove itests due to unavailable dependencies
Patch2:           remove-itests.patch
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:        noarch

BuildRequires:    java-devel >= 0:1.6.0
BuildRequires:    jpackage-utils
BuildRequires:    maven2 >= 2.2.1
BuildRequires:    felix-osgi-core
BuildRequires:    felix-osgi-compendium
BuildRequires:    geronimo-parent-poms
BuildRequires:    maven-resources-plugin
BuildRequires:    maven-surefire-provider-junit4

Requires:         java >= 0:1.6.0
Requires:         jpackage-utils
Requires:         felix-osgi-core
Requires:         felix-osgi-compendium
Requires(post):   jpackage-utils
Requires(postun): jpackage-utils

Provides:         geronimo-osgi-locator = %{version}-%{release}
Provides:         geronimo-osgi-registry = %{version}-%{release}

%description
This project is a set of bundles and integration tests for implementing
OSGi-specific lookup in the Geronimo spec projects.
    

%package javadoc
Group:            Development/Java
Summary:          Javadoc for %{name}
Requires:         jpackage-utils

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q
iconv -f iso8859-1 -t utf-8 LICENSE > LICENSE.conv && mv -f LICENSE.conv LICENSE
sed -i 's/\r//' LICENSE 
%patch1 -p0
%patch2 -p0

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mvn-jpp \
        -e \
        -Dmaven2.jpp.mode=true \
        -Dmaven2.jpp.depmap.file="%{SOURCE1}" \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        install javadoc:aggregate

%install
rm -rf %{buildroot}

# jars
install -d -m 0755 %{buildroot}%{_javadir}
install -m 644 %{registry}/target/%{registry}-%{version}.jar %{buildroot}%{_javadir}/%{registry}-%{version}.jar
install -m 644 %{locator}/target/%{locator}-%{version}.jar %{buildroot}%{_javadir}/%{locator}-%{version}.jar

(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; \
    do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

%add_to_maven_depmap org.apache.geronimo.specs %{name} %{version} JPP %{name}
%add_to_maven_depmap org.apache.geronimo.specs %{registry} %{version} JPP %{registry}
%add_to_maven_depmap org.apache.geronimo.specs %{locator} %{version} JPP %{locator}


# poms
install -d -m 0755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom
install -pm 644 %{registry}/pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{registry}.pom
install -pm 644 %{locator}/pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{locator}.pom

# javadoc
install -d -m 0755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr target/site/api*/* %{buildroot}%{_javadocdir}/%{name}-%{version}/
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE
%{_javadir}/*
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*

%files javadoc
%defattr(-,root,root,-)
%doc LICENSE
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

