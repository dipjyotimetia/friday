class Friday < Formula
    include Language::Python::Virtualenv
    
    desc "AI Test Case Generator CLI"
    homepage "https://github.com/dipjyotimetia/friday"
    url "https://github.com/dipjyotimetia/friday/archive/refs/tags/[LATEST_VERSION].tar.gz"
    sha256 "[SHA256_OF_TAR]"
    license "MIT"
  
    depends_on "python@3.13"
    depends_on "poetry"
  
    def install
      virtualenv_install_with_resources
    end
  
    test do
      assert_match "friday version", shell_output("#{bin}/friday version")
    end
  end