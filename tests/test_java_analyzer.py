"""Tests for Java language analyzer"""
import pytest
from src.language_analyzers.java_analyzer import JavaAnalyzer


class TestJavaAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        return JavaAnalyzer()
    
    def test_file_extensions(self, analyzer):
        assert analyzer.get_file_extensions() == ['.java']
    
    def test_language_name(self, analyzer):
        assert analyzer.get_language_name() == 'Java'
    
    def test_extract_classes(self, analyzer):
        code = '''
public class Animal {
    private String name;
    
    public Animal(String name) {
        this.name = name;
    }
}

public abstract class Mammal extends Animal {
    public abstract void makeSound();
}

interface Walkable {
    void walk();
}

enum Status {
    ACTIVE, INACTIVE, PENDING
}
'''
        classes = analyzer._extract_classes(code)
        class_names = [c['name'] for c in classes]
        
        assert 'Animal' in class_names
        assert 'Mammal' in class_names
        assert 'Walkable' in class_names
        assert 'Status' in class_names
    
    def test_extract_methods(self, analyzer):
        code = '''
public class Calculator {
    
    public int add(int a, int b) {
        return a + b;
    }
    
    private static double multiply(double x, double y) {
        return x * y;
    }
    
    protected synchronized void updateCache() throws IOException {
        // Update cache
    }
    
    public Calculator() {
        // Constructor
    }
}
'''
        methods = analyzer._extract_methods(code)
        method_names = [m['name'] for m in methods]
        
        assert 'add' in method_names
        assert 'multiply' in method_names
        assert 'updateCache' in method_names
        assert 'Calculator' in method_names  # Constructor
    
    def test_extract_fields(self, analyzer):
        code = '''
public class User {
    private String username;
    private int age = 0;
    public static final String DEFAULT_ROLE = "USER";
    protected volatile boolean isActive;
    transient String sessionId;
}
'''
        fields = analyzer._extract_fields(code)
        
        assert 'username' in fields
        assert 'age' in fields
        assert 'DEFAULT_ROLE' in fields
        assert 'isActive' in fields
        assert 'sessionId' in fields
    
    def test_javadoc_coverage(self, analyzer):
        code = '''
public class MathUtils {
    
    /**
     * Calculates the sum of two integers.
     * @param a the first integer
     * @param b the second integer
     * @return the sum of a and b
     */
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
}
'''
        metrics = analyzer.analyze_file('Test.java', code)
        
        assert metrics['documentacion']['cobertura'] == 0.5  # 1 of 2 methods documented
    
    def test_error_handling(self, analyzer):
        code = '''
public class FileProcessor {
    
    public String readFile(String path) {
        try {
            return Files.readString(Paths.get(path));
        } catch (IOException e) {
            logger.error("Error reading file", e);
            return null;
        }
    }
    
    public void writeFile(String path, String content) throws IOException {
        Files.writeString(Paths.get(path), content);
    }
    
    public void deleteFile(String path) {
        new File(path).delete();
    }
}
'''
        metrics = analyzer.analyze_file('Test.java', code)
        
        assert metrics['manejo_errores']['cobertura'] > 0  # Has error handling
    
    def test_test_detection(self, analyzer):
        code = '''
import org.junit.Test;
import org.junit.Before;

public class CalculatorTest {
    
    private Calculator calculator;
    
    @Before
    public void setUp() {
        calculator = new Calculator();
    }
    
    @Test
    public void testAddition() {
        assertEquals(5, calculator.add(2, 3));
    }
    
    @Test
    public void testSubtraction() {
        assertEquals(2, calculator.subtract(5, 3));
    }
}

class TestMathUtils {
    public void testMultiplication() {
        // Test method
    }
}
'''
        metrics = analyzer.analyze_file('Test.java', code)
        
        assert metrics['pruebas']['cobertura'] > 0  # Has test methods and classes
    
    def test_security_patterns(self, analyzer):
        dangerous_code = '''
public class CommandExecutor {
    public void execute(String command) {
        Runtime.getRuntime().exec(command);
        System.out.println("Executing: " + command);
    }
    
    public void processFile(String path) {
        new File(path).delete();
    }
}
'''
        
        safe_code = '''
public class UserValidator {
    public boolean validateEmail(@NotNull String email) {
        if (email == null || email.isEmpty()) {
            return false;
        }
        return email.matches("^[A-Za-z0-9+_.-]+@(.+)$");
    }
    
    public PreparedStatement createQuery(Connection conn, String userId) throws SQLException {
        String sql = "SELECT * FROM users WHERE id = ?";
        PreparedStatement stmt = conn.prepareStatement(sql);
        stmt.setString(1, userId);
        return stmt;
    }
}
'''
        
        dangerous_metrics = analyzer.analyze_file('Test.java', dangerous_code)
        safe_metrics = analyzer.analyze_file('Test.java', safe_code)
        
        assert dangerous_metrics['seguridad']['validacion'] < safe_metrics['seguridad']['validacion']
    
    def test_complexity_calculation(self, analyzer):
        simple_code = '''
public class Simple {
    public int getValue() {
        return 42;
    }
}
'''
        
        complex_code = '''
public class Complex {
    public int process(int[] data) {
        int result = 0;
        for (int i = 0; i < data.length; i++) {
            if (data[i] > 0) {
                if (data[i] % 2 == 0) {
                    result += data[i];
                } else if (data[i] % 3 == 0) {
                    result -= data[i];
                }
            } else {
                switch (data[i]) {
                    case -1:
                        result *= 2;
                        break;
                    case -2:
                        result /= 2;
                        break;
                    default:
                        result = 0;
                }
            }
        }
        return result > 0 ? result : 0;
    }
}
'''
        
        simple_metrics = analyzer.analyze_file('Test.java', simple_code)
        complex_metrics = analyzer.analyze_file('Test.java', complex_code)
        
        assert simple_metrics['complejidad']['ciclomatica'] > complex_metrics['complejidad']['ciclomatica']
    
    def test_style_consistency(self, analyzer):
        good_style = '''
public class WellFormatted {
    private String name;
    private int age;
    
    public WellFormatted(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() {
        return name;
    }
    
    public int getAge() {
        return age;
    }
}
'''
        
        poor_style = '''
public class poorlyFormatted
{
private String Name;
    private int AGE;
    
public poorlyFormatted(String n,int a)
{
this.Name=n;
        this.AGE=a;}
        
    public String get_name(){
return Name;
    }
}
'''
        
        good_metrics = analyzer.analyze_file('Test.java', good_style)
        poor_metrics = analyzer.analyze_file('Test.java', poor_style)
        
        assert good_metrics['consistencia_estilo']['consistencia'] > poor_metrics['consistencia_estilo']['consistencia']